```sql
WITH ranked_signees AS (
    SELECT id,
           ROW_NUMBER() OVER (ORDER BY id) AS rn
    FROM "Signee"
)
DELETE FROM "Signee"
WHERE id IN (
    SELECT id FROM ranked_signees WHERE rn > 5
);
```