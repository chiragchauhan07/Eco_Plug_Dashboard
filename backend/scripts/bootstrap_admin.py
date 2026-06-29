import argparse
import asyncio
import sys

from sqlalchemy.future import select

from app.core.security import hash_password
from app.database.session import async_session_maker
from app.models.dashboard import DashboardAdminUser


async def bootstrap_super_admin(email: str, password: str, full_name: str) -> bool:
    """
    Bootstrap the initial Super Admin user if no administrator exists.
    """
    async with async_session_maker() as session:
        # Check if any administrator already exists
        result = await session.execute(select(DashboardAdminUser))
        any_admin = result.scalars().first()

        if any_admin is not None:
            print(
                "Error: An administrator already exists in the database. Refusing to bootstrap.",
                file=sys.stderr,
            )
            return False

        # Hash password using Argon2 via core security helper
        pw_hash = hash_password(password)

        super_admin = DashboardAdminUser(
            email=email,
            password_hash=pw_hash,
            full_name=full_name,
            role="SuperAdmin",
            is_active=True,
        )
        session.add(super_admin)
        await session.commit()

        print(
            f"Success: Initial Super Admin '{full_name}' ({email}) created successfully."
        )
        return True


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Bootstrap the initial dashboard Super Admin."
    )
    parser.add_argument(
        "--email", required=True, help="Email address of the super admin"
    )
    parser.add_argument("--password", required=True, help="Password of the super admin")
    parser.add_argument("--name", required=True, help="Full name of the super admin")

    args = parser.parse_args()

    success = asyncio.run(bootstrap_super_admin(args.email, args.password, args.name))
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
