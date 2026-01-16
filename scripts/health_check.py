#!/usr/bin/env python3
"""
Health check script for ARES - useful for monitoring and alerts.
"""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx
from loguru import logger

# Configure logger
logger.remove()
logger.add(sys.stderr, level="ERROR")  # Only show errors


def check_health(api_url: str, timeout: int = 10) -> dict:
    """Check ARES health status."""
    try:
        with httpx.Client(timeout=timeout) as client:
            response = client.get(f"{api_url}/health")
            response.raise_for_status()
            return response.json()
    except httpx.TimeoutException:
        return {"status": "timeout", "error": "Request timed out"}
    except httpx.ConnectError:
        return {"status": "unreachable", "error": "Cannot connect to API"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def check_services(health_data: dict) -> dict:
    """Check individual service status."""
    services_status = {
        "all_healthy": True,
        "services": {},
    }

    if "services" in health_data:
        for service_name, service_info in health_data["services"].items():
            is_healthy = service_info.get("status") == "healthy"
            services_status["services"][service_name] = {
                "healthy": is_healthy,
                "status": service_info.get("status", "unknown"),
            }
            if not is_healthy:
                services_status["all_healthy"] = False

    return services_status


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="ARES Health Check")
    parser.add_argument(
        "--api-url",
        type=str,
        default="http://localhost:8000",
        help="ARES API URL (default: http://localhost:8000)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="Request timeout in seconds (default: 10)",
    )
    parser.add_argument(
        "--exit-code",
        action="store_true",
        help="Exit with non-zero code if unhealthy",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON format",
    )

    args = parser.parse_args()

    # Check health
    health_data = check_health(args.api_url, args.timeout)

    if args.json:
        import json
        print(json.dumps(health_data, indent=2))
    else:
        status = health_data.get("status", "unknown")
        if status == "healthy":
            print("✅ ARES is healthy")
            if "services" in health_data:
                services = check_services(health_data)
                for service_name, service_info in services["services"].items():
                    icon = "✅" if service_info["healthy"] else "❌"
                    print(f"  {icon} {service_name}: {service_info['status']}")
        else:
            print(f"❌ ARES is unhealthy: {health_data.get('error', 'Unknown error')}")

    # Exit code
    if args.exit_code:
        is_healthy = health_data.get("status") == "healthy"
        if "services" in health_data:
            services = check_services(health_data)
            is_healthy = services["all_healthy"]
        sys.exit(0 if is_healthy else 1)


if __name__ == "__main__":
    main()
