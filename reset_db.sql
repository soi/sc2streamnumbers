DELETE FROM main_streamnumber;
DELETE FROM main_stream;
DELETE FROM main_interval;
DELETE FROM main_streamtype;
DELETE FROM main_streamnumbertype;
DELETE FROM main_streamingplatform;
DELETE FROM main_rating;

SELECT pg_catalog.setval('main_streamnumbertype_id_seq', 3, true);
SELECT pg_catalog.setval('main_streamtype_id_seq', 1, true);
SELECT pg_catalog.setval('main_rating_id_seq', 1, true);
SELECT pg_catalog.setval('main_streamingplatform_id_seq', 1, true);

INSERT INTO main_streamnumbertype (id, name, number_count) VALUES
(1, 'hour', 1),
(2, 'day', 6), -- avg over half an hour
(3, 'week', 8), -- a week dataset is avg(8 day data sets)
(4, 'month', 6); -- a week dataset is avg(8 day data sets)

INSERT INTO main_streamtype (id, name) VALUES (1, 'Default');
INSERT INTO main_streamingplatform (id, name) VALUES (1, 'Default');
INSERT INTO main_rating (id, name) VALUES (1, 'Default');
