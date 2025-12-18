async def test_connection():
    conn = await get_connection()
    value = await conn.fetchval("SELECT 1")
    await conn.close()
    print("DB OK:", value)