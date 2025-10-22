-- Season seed (set the actual year you want, e.g., 2025)
INSERT INTO seasons (year, is_current)
VALUES (2025, TRUE)
ON CONFLICT (year) DO NOTHING;

-- JSON templates (we’ll keep them inline for now)
-- Default roster schema
WITH roster AS (
  SELECT jsonb_build_object(
    'QB', 1, 'RB', 2, 'K', 1, 'DEF', 1, 'WR', 2, 'FLEX_RB_WR', 1, 'TE', 1,
    'BENCH', 6, 'IR', 3
  ) AS j
),
scoring AS (
  SELECT jsonb_build_object(
    'passing_yards_per_point', 25,
    'passing_td', 4,
    'interception', -2,
    'rushing_yards_per_point', 10,
    'reception', 1,
    'receiving_yards_per_point', 10,
    'rush_recv_td', 6,
    'sack', 1,
    'def_interception', 2,
    'fumble_recovered', 2,
    'safety', 2,
    'any_td', 6,
    'team_def_2pt_return', 2,
    'pat_made', 1,
    'fg_made_0_50', 3,
    'fg_made_50_plus', 5,
    'points_allowed_le_10', 5,
    'points_allowed_le_20', 2,
    'points_allowed_le_30', 0,
    'points_allowed_gt_30', -2
  ) AS j
)
-- Nothing is inserted into leagues here; these JSONs will be used by API when creating a league.
SELECT 1;
