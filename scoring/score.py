STARTING_ZONES_BY_LETTER = {
    'G': 0,
    'O': 1,
    'P': 2,
    'Y': 3,
}


class Scorer:
    # Assumption: we will trust the *ordering* of the entries in the data we
    # are given and *ignore* the actual 'time' values. We defer handling of
    # equivalent-time operations to the token controller.

    def __init__(self, teams_data, arena_data):
        self._starting_zone_to_tla = {
            info['zone']: tla
            for tla, info in teams_data.items()
        }

        self._team_info = teams_data

        self._scoring_zones = arena_data['arena_zones']

    def calculate_scores(self):
        points_per_team = {
            tla: 0
            for tla in self._team_info
        }

        # Point for movement
        for tla, info in self._team_info.items():
            if info.get('moved'):
                points_per_team[tla] += 1

        # Scoring zone weighting
        weight_by_scoring_zone_and_starting_zone = {
            (scoring_zone, starting_zone): 0
            for scoring_zone in range(9)
            for starting_zone in range(4)
        }

        # Add up the weights
        for scoring_zone, scoring_zone_configuration in self._scoring_zones.items():
            for weighting, letter in (
                [(1, letter) for letter in scoring_zone_configuration['partial']] +
                [(2, letter) for letter in scoring_zone_configuration['full']]
            ):
                starting_zone = STARTING_ZONES_BY_LETTER[letter]
                weight_by_scoring_zone_and_starting_zone[scoring_zone, starting_zone] += weighting

        # Compute the maximum weight per scoring zone
        maximum_weight_by_scoring_zone = {
            scoring_zone: max(
                weight_by_scoring_zone_and_starting_zone[scoring_zone, starting_zone]
                for starting_zone in range(4)
            )
            for scoring_zone in range(9)
        }

        # Peak starting zones by scoring zone
        peak_starting_zones_by_scoring_zone = {n: [] for n in range(9)}

        for scoring_zone in range(9):
            for starting_zone in range(4):
                if (
                    weight_by_scoring_zone_and_starting_zone[scoring_zone, starting_zone] ==
                    maximum_weight_by_scoring_zone[scoring_zone]
                ) and (
                    maximum_weight_by_scoring_zone[scoring_zone] > 0
                ):
                    peak_starting_zones_by_scoring_zone[scoring_zone].append(starting_zone)
    
        # Peak teams by scoring zone
        peak_teams_by_scoring_zone = {
            scoring_zone: [
                self._starting_zone_to_tla[x] for x in peak_starting_zones
            ]
            for scoring_zone, peak_starting_zones in peak_starting_zones_by_scoring_zone.items()
        }

        # Number of owned zones by team
        owned_zone_count_by_team = {
            tla: 0
            for tla in self._team_info
        }

        for scoring_zone, peak_teams in peak_teams_by_scoring_zone.items():
            for peak_team in peak_teams:
                owned_zone_count_by_team[peak_team] += 1

        # Owned zone score
        owned_zone_score_by_team = {
            team: zone_count ** 2
            for team, zone_count in owned_zone_count_by_team.items()
        }
    
        for team in self._team_info:
            points_per_team[team] += owned_zone_score_by_team[team]

        return points_per_team


if __name__ == '__main__':
    import libproton
    libproton.main(Scorer)
