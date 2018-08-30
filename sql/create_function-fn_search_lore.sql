CREATE OR REPLACE FUNCTION manifest.fn_search_lore (p_lore_type VARCHAR, p_lore_search VARCHAR)
  RETURNS SETOF RECORD AS
$BODY$
BEGIN

	IF UPPER(p_lore_type) = 'GRIMOIRE' THEN
	RETURN QUERY
		SELECT JSONB_BUILD_OBJECT(
			'hash',
			json->>'cardId',
			'item_type',
			'Grimoire',
			'item_name',
			json->'cardName',
			'item_icon',
			'https://www.bungie.net' || (json->'highResolution'->'image'->>'sheetPath')::TEXT,
			'item_screenshot',
			'https://www.bungie.net' || (json->'highResolution'->'image'->>'sheetPath')::TEXT,
			'item_description',
			json->'cardIntro',
			'lore_subtitle',
			json->'cardIntro',
			'lore_name',
			json->'cardName',
			'lore_description',
			json->'cardDescription'
			) lore_entry
		FROM manifest.t_manifest tm
		WHERE tm.table_name = 'DestinyGrimoireCardDefinition'
		AND tm.deleted IS NOT NULL
		AND to_tsvector('english',
			(json->>'cardName')::TEXT || ' ' ||
			COALESCE((json->>'cardIntro')::TEXT, '') || ' ' ||
			(json->>'cardDescription')::TEXT
		) @@ to_tsquery('english', p_lore_search) = TRUE
		ORDER BY tm.json->>'cardName'
		;
	ELSIF UPPER(p_lore_type) = 'INVENTORY' THEN
	RETURN QUERY
		SELECT
				JSONB_BUILD_OBJECT (
					'hash',
					diid.json->>'hash',
					'item_type',
					'Lore',
					'item_name',
					diid.json->'displayProperties'->>'name',
					'item_icon',
					'https://www.bungie.net' || (diid.json->'displayProperties'->>'icon')::TEXT,
					'item_screenshot',
					'https://www.bungie.net' || (diid.json->>'screenshot')::TEXT,
					'item_description',
					diid.json->'displayProperties'->>'description',
					'lore_subtitle',
					dld.json->>'subtitle',
					'lore_name',
					dld.json->'displayProperties'->>'name',
					'lore_description',
					dld.json->'displayProperties'->'description'
				) lore_entry
			FROM manifest.t_manifest diid, manifest.t_manifest dld
			WHERE diid.table_name = 'DestinyInventoryItemDefinition'
			AND dld.table_name = 'DestinyLoreDefinition'
			AND diid.deleted IS NULL
			AND dld.deleted IS NULL
			AND diid.json->'itemCategoryHashes' @> '[3109687656]'::JSONB = FALSE
			AND diid.json->>'loreHash' = dld.json->>'hash'
			AND (
				to_tsvector('english',
					(dld.json->'displayProperties'->>'description')::TEXT || ' ' ||
					(dld.json->>'subtitle')::TEXT || ' ' ||
					(dld.json->'displayProperties'->>'name')::TEXT
				) @@ to_tsquery('english', p_lore_search) = TRUE
			)
			ORDER BY diid.json->'displayProperties'->>'name';
	ELSIF UPPER(p_lore_type) = 'RECORDS' THEN
	RETURN QUERY
	    SELECT
            JSONB_BUILD_OBJECT(
                'hash',
                drd.json->>'hash',
                'item_type',
                'Record',
                'item_name',
                drd.json->'displayProperties'->>'name',
                'item_icon',
                'https://www.bungie.net' || (drd.json->'displayProperties'->>'icon')::TEXT,
                'item_screenshot',
                'https://www.bungie.net' || (drd.json->'displayProperties'->>'icon')::TEXT,
                'item_description',
                dld.json->>'subtitle',
                'lore_subtitle',
                dld.json->>'subtitle',
                'lore_name',
                dld.json->'displayProperties'->>'name',
                'lore_description',
                dld.json->'displayProperties'->>'description'
            ) lore_entry
        FROM manifest.mv_manifest drd, manifest.mv_manifest dld
        WHERE drd.table_name = 'DestinyRecordDefinition' AND dld.table_name = 'DestinyLoreDefinition'
            AND (drd.json->>'redacted')::BOOLEAN = False
            AND drd.json->'displayProperties'->>'name' != ''
            -- AND drd.json ? 'loreHash'
            AND dld.json->>'hash' = drd.json->>'loreHash'
            AND (
                to_tsvector('english',
                    (dld.json->'displayProperties'->>'name')::TEXT || ' ' ||
                    COALESCE((dld.json->>'subtitle')::TEXT || ' ', '') ||
                    (dld.json->'displayProperties'->>'description')::TEXT
                ) @@ to_tsquery('english', p_lore_search) = TRUE
            )
        ORDER BY drd.json->'displayProperties'->>'name';
	END IF;

	RETURN;

	--EXCEPTION
		--WHEN OTHERS THEN
			--RAISE NOTICE 'Invalid input';
			--RETURN QUERY SELECT ('{"error":"invalid input"}')::JSONB;
END
$BODY$
  LANGUAGE plpgsql;