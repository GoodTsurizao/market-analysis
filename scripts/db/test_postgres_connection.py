from postgres_connector import connect_postgres, get_postgres_config


def main():
    config = get_postgres_config()
    print("Connecting with:", config.to_dsn())

    with connect_postgres() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT current_database(), current_user, version()")
            database_name, user_name, version = cur.fetchone()

    print("PostgreSQL connection succeeded.")
    print(f"database={database_name}")
    print(f"user={user_name}")
    print(f"version={version}")


if __name__ == "__main__":
    main()
