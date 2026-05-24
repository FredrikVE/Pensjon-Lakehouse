SELECT
    aldersgruppe,
    aldersgruppe_sortering,
    befolkning,
    andel
FROM ${catalog}.${schema}.aldersgruppe_fordeling
ORDER BY aldersgruppe_sortering
