ATTACH TABLE _ UUID '59b50cfe-7a3f-4e69-bd3b-d86f414fb58a'
(
    `window_start` DateTime,
    `window_end` DateTime,
    `product_id` String,
    `average_price` Float64
)
ENGINE = MergeTree
ORDER BY window_start
SETTINGS index_granularity = 8192
