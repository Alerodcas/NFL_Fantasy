DO
$$
DECLARE
    rec RECORD;
BEGIN
    -- Disable referential integrity temporarily
    EXECUTE 'SET session_replication_role = replica';
    
    -- Loop through all tables in the public schema
    FOR rec IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public')
    LOOP
        EXECUTE 'DROP TABLE IF EXISTS public.' || quote_ident(rec.tablename) || ' CASCADE';
    END LOOP;
    
    -- Re-enable referential integrity
    EXECUTE 'SET session_replication_role = DEFAULT';
END;
$$;
