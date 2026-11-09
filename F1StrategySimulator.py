from unittest import result

import oracledb
import requests


class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.cursor = None

    def connect(self):
        self.connection = oracledb.connect(
            user="system",
            password="*****",
            host="localhost",
            port=1522,
            service_name="FREEPDB1"
        )

        self.cursor = self.connection.cursor()

    def disconnect(self):
        self.cursor.close()
        self.connection.close()

    def get_drivers(self):
        self.cursor.execute("SELECT driver_name, team FROM DRIVERS")
        drivers = self.cursor.fetchall()
        return drivers

    
    def get_driver(self, driver_input):
        self.cursor.execute(
            """
            SELECT driver_id, driver_name, team
            FROM DRIVERS
            WHERE LOWER(TRIM(driver_name)) = LOWER(TRIM(:driver_name))
            """,
            driver_name=driver_input
        )

        return self.cursor.fetchone()


    
    def get_driver_by_id(self, driver_id):
        self.cursor.execute(
            """
            SELECT driver_id, driver_name, team
            FROM DRIVERS
            WHERE driver_id = :driver_id
            """,
            driver_id=driver_id
        )
        return self.cursor.fetchone()


    def get_race_by_circuit(self, circuit_id):
        self.cursor.execute(
            """
            SELECT race_id, race_name, circuit_id, race_year, total_laps
            FROM RACES
            WHERE circuit_id = :circuit_id
            AND race_year = 2026
            FETCH FIRST 1 ROW ONLY
            """,
            circuit_id=circuit_id
        )
        return self.cursor.fetchone()


    def get_circuits(self):
        self.cursor.execute("SELECT circuit_id, circuit_name, circuit_location FROM CIRCUITS")
        circuits = self.cursor.fetchall()
        return circuits

    
    def get_circuit(self, circuit_id):
        self.cursor.execute("SELECT * FROM CIRCUITS WHERE circuit_id = :placeholder",
        placeholder = circuit_id)
        circuit = self.cursor.fetchone()
        return circuit

    
    def get_circuit_by_name(self, circuit_input):
        self.cursor.execute(
            """
            SELECT circuit_id, circuit_name
            FROM CIRCUITS
            WHERE LOWER(TRIM(circuit_name)) = LOWER(TRIM(:circuit_input))
            OR LOWER(TRIM(circuit_location)) = LOWER(TRIM(:circuit_input))
            """,
            circuit_input=circuit_input
        )

        return self.cursor.fetchone()
    

    def get_race(self, race_input):
        self.cursor.execute("SELECT * FROM RACES WHERE race_name = :placeholder",
        placeholder = race_input)
        race = self.cursor.fetchone()
        return race

    def get_tyres(self):
        self.cursor.execute("SELECT * FROM TYRES")
        tyres = self.cursor.fetchall()
        return tyres

    def get_driver_history(self, driver_id, circuit_id):
        self.cursor.execute(
            "SELECT average_lap_time, average_starting_position, average_finishing_position FROM driver_circuit_history"
            " WHERE driver_id = :driver_id AND circuit_id = :circuit_id",
            driver_id = driver_id,
            circuit_id = circuit_id
        )
        driver_and_circuit = self.cursor.fetchone()
        return driver_and_circuit

    def get_team_history(self, team, circuit_id):
        self.cursor.execute(
            "SELECT team_average_lap_time FROM TEAM_CIRCUIT_HISTORY WHERE team = :team AND circuit_id = :circuit_id",
            team = team,
            circuit_id = circuit_id
        )
        team_average_lap_time = self.cursor.fetchone()
        return team_average_lap_time

    
    def save_driver_history(self, driver_id, circuit_id, average_lap_time, average_starting_position, average_finishing_position):
        self.cursor.execute(
            """
            MERGE INTO DRIVER_CIRCUIT_HISTORY target
            USING (
                SELECT :driver_id AS driver_id,
                    :circuit_id AS circuit_id
                FROM dual
            ) source
            ON (
                target.driver_id = source.driver_id
                AND target.circuit_id = source.circuit_id
            )
            WHEN MATCHED THEN
                UPDATE SET
                    target.average_lap_time = :average_lap_time,
                    target.average_starting_position = :average_starting_position,
                    target.average_finishing_position = :average_finishing_position
            WHEN NOT MATCHED THEN
                INSERT (
                    history_id, driver_id, circuit_id,
                    average_lap_time, average_starting_position,
                    average_finishing_position
                )
                VALUES (
                    DRIVER_HISTORY_SEQ.NEXTVAL, source.driver_id,
                    source.circuit_id, :average_lap_time,
                    :average_starting_position, :average_finishing_position
                )
            """,
            {
                "driver_id": driver_id,
                "circuit_id": circuit_id,
                "average_lap_time": average_lap_time,
                "average_starting_position": average_starting_position,
                "average_finishing_position": average_finishing_position
            }
        )

        self.connection.commit()


    
    def save_team_history(self, team, circuit_id, team_average_lap_time):
        self.cursor.execute(
            """
            MERGE INTO TEAM_CIRCUIT_HISTORY target
            USING (
                SELECT :team AS team,
                    :circuit_id AS circuit_id
                FROM dual
            ) source
            ON (
                target.team = source.team
                AND target.circuit_id = source.circuit_id
            )
            WHEN MATCHED THEN
                UPDATE SET
                    target.team_average_lap_time = :team_average_lap_time
            WHEN NOT MATCHED THEN
                INSERT (
                    team_history_id, team, circuit_id,
                    team_average_lap_time
                )
                VALUES (
                    TEAM_CIRCUIT_SEQ.NEXTVAL, source.team,
                    source.circuit_id, :team_average_lap_time
                )
            """,
            {
                "team": team,
                "circuit_id": circuit_id,
                "team_average_lap_time": team_average_lap_time
            }
        )

        self.connection.commit()


    def get_all_driver_records(self):
        self.cursor.execute(
            "SELECT driver_id, driver_name, team FROM DRIVERS"
        )
        return self.cursor.fetchall()


class openf1API:
    def __init__(self):
        self.base_url = "https://api.openf1.org/v1"

    def get_race_sessions(self, year, country):

        url = self.base_url + "/sessions"

        params = {
            "year": year,
            "country_name": country,
            "session_name": "Race"
        }

        response = requests.get(url, params=params)

        data = response.json()

        return data

    
    def get_lap_data(self, session_key):

        url = self.base_url + "/laps"

        params = {
         "session_key": session_key
        }

        response = requests.get(url, params=params)

        lap_data = response.json()

        return lap_data


    def get_race_control_data(self, session_key):

        url = self.base_url + "/race_control"

        params = {
            "session_key": session_key
        }

        response = requests.get(url, params=params)

        race_control_data = response.json()

        return race_control_data

    def get_stint_data(self, session_key):

        url = self.base_url + "/stints"

        params = {
            "session_key": session_key
        }

        response = requests.get(url, params=params)

        stint_data = response.json()

        return stint_data

    def get_starting_grid_data(self, session_key):

        url = self.base_url + "/starting_grid"

        params = {
            "session_key": session_key
        }

        response = requests.get(url, params=params)

        starting_grid_data = response.json()

        return starting_grid_data


    def get_session_result_data(self, session_key):

        url = self.base_url + "/session_result"

        params = {
            "session_key": session_key
        }

        response = requests.get(url, params=params)

        session_result_data = response.json()

        return session_result_data

    def get_driver_data(self, session_key):

        url = self.base_url + "/drivers"

        params = {
            "session_key": session_key
        }

        response = requests.get(url, params=params)

        driver_data = response.json()

        return driver_data



class HistoricalDataImporter:

    def __init__(self):
        pass

    
    def collect_historical_data(self, api, country, circuit_short_name, database, years=(2025, 2026)):

        from datetime import datetime, timezone

        combined_usable_laps = []
        combined_starting_grid = []
        combined_session_results = []
        combined_driver_data = []

        # Match drivers to their existing Oracle SQL IDs.
        driver_ids = {}

        for driver_id, driver_name, team in database.get_all_driver_records():
            driver_ids[driver_name.upper()] = driver_id

        for year in years:
            race_sessions = api.get_race_sessions(year, country)

            for session in race_sessions:

                # Only collect races from the requested circuit.
                if session.get('circuit_short_name', '').lower() != circuit_short_name.lower():
                    continue

                # Skip races that have not finished yet.
                session_end = session.get('date_end')
                if not session_end:
                    continue

                end_date = datetime.fromisoformat(
                    session_end.replace('Z', '+00:00')
                )

                if end_date > datetime.now(timezone.utc):
                    continue

                session_key = session['session_key']
                print("Year:", year, "Session key:", session_key)

                lap_data = api.get_lap_data(session_key)
                race_control_data = api.get_race_control_data(session_key)
                stint_data = api.get_stint_data(session_key)
                starting_grid_data = api.get_starting_grid_data(session_key)
                print("Starting grid response:", starting_grid_data[:2] if isinstance(starting_grid_data, list) else starting_grid_data)
                session_result_data = api.get_session_result_data(session_key)
                driver_data = api.get_driver_data(session_key)

                if not lap_data or not session_result_data or not driver_data:
                    continue

                # Filter this race before combining it with other races.
                usable_laps = self.filter_laps(
                    lap_data, race_control_data, stint_data
                )

                # Connect original driver numbers to driver identities.
                driver_mapping = {}
                team_mapping = {}

                for driver in driver_data:
                    driver_name = driver['full_name']
                    original_number = driver['driver_number']
                    team_name = driver['team_name']

                    historical_id = driver_ids.get(driver_name.upper())

                    if historical_id is None:
                        continue

                    driver_mapping[original_number] = historical_id
                    team_mapping[original_number] = team_name

                    updated_driver = driver.copy()
                    updated_driver['driver_number'] = historical_id

                    combined_driver_data.append(updated_driver)

                # Only include drivers who completed this race.
                completed_drivers = set()

                for result in session_result_data:
                    if (
                        result.get('dnf') is False
                        and result.get('dns') is not True
                        and result.get('dsq') is not True
                    ):
                        completed_drivers.add(result['driver_number'])

                # Combine usable laps, preserving the team for each race.
                for lap in usable_laps:
                    original_number = lap['driver_number']

                    if (
                        original_number in driver_mapping
                        and original_number in completed_drivers
                    ):
                        updated_lap = lap.copy()
                        updated_lap['driver_number'] = driver_mapping[original_number]
                        updated_lap['team_name'] = team_mapping[original_number]

                        combined_usable_laps.append(updated_lap)

                # Combine starting positions.
                for starting in starting_grid_data:
                    original_number = starting['driver_number']

                    if (
                        original_number in driver_mapping
                        and original_number in completed_drivers
                    ):
                        updated_starting = starting.copy()
                        updated_starting['driver_number'] = driver_mapping[original_number]

                        combined_starting_grid.append(updated_starting)

                # Combine finishing results.
                for result in session_result_data:
                    original_number = result['driver_number']

                    if original_number in driver_mapping:
                        updated_result = result.copy()
                        updated_result['driver_number'] = driver_mapping[original_number]

                        combined_session_results.append(updated_result)

        return {
            'usable_laps': combined_usable_laps,
            'starting_grid_data': combined_starting_grid,
            'session_result_data': combined_session_results,
            'driver_data': combined_driver_data,
            'driver_ids': driver_ids
        }


    
    def filter_laps(self, lap_data, race_control_data, stint_data):
        usable_laps = []

        safety_car_laps = set()
        safety_car_start = None
        virtual_safety_car_start = None

        for message in race_control_data:
            message_text = message.get('message', '')
            lap_number = message.get('lap_number')

            if lap_number is None:
                continue

            if message_text == "VIRTUAL SAFETY CAR DEPLOYED":
                virtual_safety_car_start = lap_number

            elif message_text == "VIRTUAL SAFETY CAR ENDING":
                if virtual_safety_car_start is not None:
                    safety_car_laps.update(
                        range(virtual_safety_car_start, lap_number + 1)
                    )
                    virtual_safety_car_start = None

            elif message_text == "SAFETY CAR DEPLOYED":
                safety_car_start = lap_number

            elif message_text == "SAFETY CAR IN THIS LAP":
                if safety_car_start is not None:
                    safety_car_laps.update(
                        range(safety_car_start, lap_number + 1)
                    )
                    safety_car_start = None

        # Exclude remaining laps if a safety car period has no ending message.
        last_lap = max(
            (lap['lap_number'] for lap in lap_data
            if lap.get('lap_number') is not None),
            default=0
        )

        for start_lap in (safety_car_start, virtual_safety_car_start):
            if start_lap is not None:
                safety_car_laps.update(range(start_lap, last_lap + 1))

        pit_out_laps = []

        for lap in lap_data:
            if lap.get('is_pit_out_lap') is True:
                drivernum_lapnum = (
                    lap['driver_number'], lap['lap_number']
                )
                pit_out_laps.append(drivernum_lapnum)

        pit_in_laps = []

        for lap in lap_data:
            if lap.get('is_pit_out_lap') is True:
                drivernum_lapnum = (
                    lap['driver_number'], lap['lap_number'] - 1
                )
                pit_in_laps.append(drivernum_lapnum)

        flagged_laps = []

        for message in race_control_data:
            flag = message.get('flag')
            lap_number = message.get('lap_number')

            if flag in ("YELLOW", "DOUBLE YELLOW", "RED"):
                if lap_number is not None:
                    flagged_laps.append(lap_number)

        wet_lap = []

        for stint in stint_data:
            if stint.get('compound') in ("WET", "INTERMEDIATE"):
                start_lap = stint.get('lap_start')
                end_lap = stint.get('lap_end')
                driver = stint.get('driver_number')

                if start_lap is not None and end_lap is not None:
                    for x in range(start_lap, end_lap + 1):
                        wet_lap.append((driver, x))

        for lap in lap_data:
            lap_number = lap.get('lap_number')
            driver_number = lap.get('driver_number')

            if (
                lap_number is not None
                and lap_number > 1
                and lap_number not in safety_car_laps
                and (driver_number, lap_number) not in pit_out_laps
                and (driver_number, lap_number) not in pit_in_laps
                and lap_number not in flagged_laps
                and (driver_number, lap_number) not in wet_lap
                and lap.get('lap_duration') is not None
            ):
                usable_laps.append(lap)

        return usable_laps


    def calculate_driver_average_lap(self, usable_laps, driver_number):
        all_laps = []

        for lap in usable_laps:
            if lap['driver_number'] == driver_number:
                laps = lap['lap_duration']
                all_laps.append(laps)

        if not all_laps:
            return None

        average_lap_time = sum(all_laps) / len(all_laps)
        return average_lap_time

    def calculate_driver_history(self, starting_grid_data, session_result_data, average_lap_time, driver_number):

        all_starting_positions = []

        for starting in starting_grid_data:
            if starting['driver_number'] == driver_number:
                starting_position = starting['position']

                if starting_position is not None:
                    all_starting_positions.append(starting_position)

        if all_starting_positions:
            average_starting_position = sum(all_starting_positions) / len(all_starting_positions)
        else:
            average_starting_position = None

        all_finishing_positions = []

        for finishing in session_result_data:
            if (
                finishing['driver_number'] == driver_number
                and finishing['dnf'] == False
                and finishing.get('dns') is not True
                and finishing.get('dsq') is not True
            ):
                finishing_position = finishing['position']

                if finishing_position is not None:
                    all_finishing_positions.append(finishing_position)

        if all_finishing_positions:
            average_finishing_position = sum(all_finishing_positions) / len(all_finishing_positions)
        else:
            average_finishing_position = None


        return average_lap_time, average_starting_position, average_finishing_position

    
    def calculate_team_average_lap(self, driver_data, usable_laps):

        team_laps = {}
        team_lap_average = {}

        for lap in usable_laps:
            team = lap['team_name']

            if team not in team_laps:
                team_laps[team] = []

            team_laps[team].append(lap['lap_duration'])

        for team in team_laps:
            average = sum(team_laps[team]) / len(team_laps[team])
            team_lap_average[team] = average

        return team_lap_average

    
    def import_circuit_history(self, api, database, country,
                            circuit_short_name, circuit_id):

        historical_data = self.collect_historical_data(
            api, country, circuit_short_name, database
        )

        usable_laps = historical_data['usable_laps']
        starting_grid_data = historical_data['starting_grid_data']
        session_result_data = historical_data['session_result_data']
        driver_data = historical_data['driver_data']
        driver_ids = historical_data['driver_ids']

        for driver_id in driver_ids.values():

            average_lap_time = self.calculate_driver_average_lap(
                usable_laps, driver_id
            )

            if average_lap_time is None:
                continue

            average_lap_time, average_start, average_finish = (
                self.calculate_driver_history(
                    starting_grid_data,
                    session_result_data,
                    average_lap_time,
                    driver_id
                )
            )

            database.save_driver_history(
                driver_id,
                circuit_id,
                average_lap_time,
                average_start,
                average_finish
            )

        team_averages = self.calculate_team_average_lap(
            driver_data, usable_laps
        )

        for team, average_lap_time in team_averages.items():
            database.save_team_history(
                team,
                circuit_id,
                average_lap_time
            )


class StrategyEngine:
    def __init__(self, database):
        self.databasemanager = database

    def get_baseline_pace(self, driver_id, team, circuit_id):

        # First, check the driver's historical lap time
        driver_history = self.databasemanager.get_driver_history(driver_id, circuit_id)

        if driver_history:
            return driver_history[0]

        # If no driver history exists, check the team's lap time
        team_history = self.databasemanager.get_team_history(team, circuit_id)

        if team_history:
            return team_history[0]

        # If neither exists, use the circuit's typical lap time
        circuit = self.databasemanager.get_circuit(circuit_id)

        return circuit[5]

    
    def estimate_tyre_life(self, compound, total_laps, circuit_id):

        tyres = self.databasemanager.get_tyres()
        circuit = self.databasemanager.get_circuit(circuit_id)

        tyre_wear_level = circuit[9]

        for tyre in tyres:
            if tyre[1] == compound:
                lifespan = (tyre[3] / 100) * total_laps

                if tyre_wear_level == "Low":
                    adjusted_lifespan = lifespan * 1.1

                elif tyre_wear_level == "Medium":
                    adjusted_lifespan = lifespan

                elif tyre_wear_level == "High":
                    adjusted_lifespan = lifespan * 0.9

                else:
                    raise ValueError("Unknown tyre wear level")

                return max(1, int(adjusted_lifespan))

        raise ValueError("Unknown tyre compound")

    
    def calculate_degradation(self, baseline_pace, tyre_age, tyre_lifespan):

        if tyre_lifespan <= 0:
            raise ValueError("Tyre lifespan must be greater than zero")

        wear_percentage = tyre_age / tyre_lifespan

        if wear_percentage <= 0.25:
            degradation_rate = 0

        elif wear_percentage <= 0.50:
            degradation_rate = 0.001

        elif wear_percentage <= 0.75:
            degradation_rate = 0.003

        elif wear_percentage <= 0.90:
            degradation_rate = 0.006

        elif wear_percentage <= 1.0:
            degradation_rate = 0.012

        else:
            degradation_rate = 0.012 + (wear_percentage - 1.0) * 0.08

        degradation = baseline_pace * degradation_rate

        return degradation


    
    def calculate_fuel_effect(self, lap_number, total_laps, race_year):

        if race_year == 2025:
            starting_fuel = 110

        elif race_year == 2026:
            starting_fuel = 70

        else:
            raise ValueError("Unsupported race year")

        fuel_per_lap = starting_fuel / total_laps

        remaining_fuel = max(
            0,
            starting_fuel - (lap_number - 1) * fuel_per_lap
        )

        fuel_effect = remaining_fuel * 0.03

        return fuel_effect

    
    def calculate_traffic_effect(self, starting_position, lap_number,
                                circuit_id, driver_id):

        circuit = self.databasemanager.get_circuit(circuit_id)
        overtaking_difficulty = circuit[10]

        if lap_number > 10:
            return 0

        if starting_position <= 5:
            traffic_penalty = 0.05

        elif starting_position <= 10:
            traffic_penalty = 0.10

        elif starting_position <= 15:
            traffic_penalty = 0.20

        else:
            traffic_penalty = 0.30

        if overtaking_difficulty == "Low":
            traffic_penalty *= 0.75

        elif overtaking_difficulty == "Medium":
            traffic_penalty *= 1.0

        elif overtaking_difficulty == "High":
            traffic_penalty *= 1.5

        else:
            raise ValueError("Unknown overtaking difficulty")

        driver_history = self.databasemanager.get_driver_history(
            driver_id, circuit_id
        )

        if driver_history:
            average_start = driver_history[1]
            average_finish = driver_history[2]

            if average_start is not None and average_finish is not None:
                positions_gained = average_start - average_finish

                adjustment = max(
                    -0.10,
                    min(0.10, positions_gained * 0.02)
                )

                traffic_penalty *= (1 - adjustment)

        return traffic_penalty

    def calculate_pit_traffic_penalty(self, circuit_id, starting_position, number_of_stops):

        circuit = self.databasemanager.get_circuit(circuit_id)
        overtaking_difficulty = circuit[10]

        if overtaking_difficulty == "Low":
            penalty_per_stop = 0.5

        elif overtaking_difficulty == "Medium":
            penalty_per_stop = 2.0

        elif overtaking_difficulty == "High":
            penalty_per_stop = 5.0

        else:
            raise ValueError("Unknown overtaking difficulty")

        if starting_position <= 5:
            position_multiplier = 1.0

        elif starting_position <= 10:
            position_multiplier = 0.8

        else:
            position_multiplier = 0.6

        total_penalty = penalty_per_stop * position_multiplier * number_of_stops

        return total_penalty


    def generate_strategy_options(self):

        from itertools import product

        compounds = ["Soft", "Medium", "Hard"]
        strategies = []

        for number_of_stints in [2, 3]:
            for combination in product(compounds, repeat=number_of_stints):

                if len(set(combination)) >= 2:
                    strategies.append(list(combination))

        return strategies


    def validate_strategy(self, strategy, total_laps, circuit_id):

        if len(strategy) < 2 or len(strategy) > 3:
            return False

        valid_compounds = {"Soft", "Medium", "Hard"}

        if any(compound not in valid_compounds for compound in strategy):
            return False

        if len(set(strategy)) < 2:
            return False

        return True


    def calculate_pit_windows(self, strategy, total_laps, circuit_id):

        tyre_lives = [
            self.estimate_tyre_life(compound, total_laps, circuit_id)
            for compound in strategy
        ]

        pit_options = []

        if len(strategy) == 2:
            for pit_lap in range(1, total_laps):

                first_stint = pit_lap
                second_stint = total_laps - pit_lap

                if (first_stint <= tyre_lives[0] * 1.3
                        and second_stint <= tyre_lives[1] * 1.3):

                    pit_options.append([pit_lap])

        elif len(strategy) == 3:
            for first_pit in range(1, total_laps - 1):
                for second_pit in range(first_pit + 1, total_laps):

                    first_stint = first_pit
                    second_stint = second_pit - first_pit
                    third_stint = total_laps - second_pit

                    if (first_stint <= tyre_lives[0] * 1.3
                            and second_stint <= tyre_lives[1] * 1.3
                            and third_stint <= tyre_lives[2] * 1.3):

                        pit_options.append([first_pit, second_pit])

        return pit_options


    def calculate_lap_time(self, baseline_pace, compound, tyre_age,
                        tyre_lifespan, lap_number, total_laps,
                        race_year, starting_position, circuit_id, driver_id):

        tyres = self.databasemanager.get_tyres()

        tyre_pace_effect = None

        for tyre in tyres:
            if tyre[1] == compound:
                tyre_pace_effect = float(tyre[2])
                break

        if tyre_pace_effect is None:
            raise ValueError("Unknown tyre compound")

        degradation = self.calculate_degradation(
            baseline_pace, tyre_age, tyre_lifespan
        )

        current_fuel_effect = self.calculate_fuel_effect(
            lap_number, total_laps, race_year
        )

        reference_fuel_effect = self.calculate_fuel_effect(
            total_laps // 2 + 1, total_laps, race_year
        )

        fuel_adjustment = current_fuel_effect - reference_fuel_effect

        traffic_effect = self.calculate_traffic_effect(
            starting_position, lap_number, circuit_id, driver_id
        )

        starting_tyre_effect = 0

        if lap_number <= 3:

            if compound == "Soft":
                starting_tyre_effect = -0.15

            elif compound == "Hard":

                if starting_position <= 5:
                    starting_tyre_effect = 0.40

                elif starting_position <= 10:
                    starting_tyre_effect = 0.30

                else:
                    starting_tyre_effect = 0.20

            starting_tyre_effect *= (4 - lap_number) / 3

        lap_time = (
            baseline_pace
            + tyre_pace_effect
            + degradation
            + fuel_adjustment
            + traffic_effect
            + starting_tyre_effect
        )

        return lap_time

    
    def simulate_strategy(self, strategy, pit_laps, baseline_pace,
                        total_laps, race_year, starting_position,
                        circuit_id, driver_id):

        circuit = self.databasemanager.get_circuit(circuit_id)
        pit_stop_time_loss = float(circuit[7])

        tyre_lives = [
            self.estimate_tyre_life(compound, total_laps, circuit_id)
            for compound in strategy
        ]

        total_race_time = 0
        current_stint = 0
        tyre_age = 0

        for lap_number in range(1, total_laps + 1):

            tyre_age += 1

            lap_time = self.calculate_lap_time(
                baseline_pace,
                strategy[current_stint],
                tyre_age,
                tyre_lives[current_stint],
                lap_number,
                total_laps,
                race_year,
                starting_position,
                circuit_id,
                driver_id
            )

            total_race_time += lap_time

            if lap_number in pit_laps:
                total_race_time += pit_stop_time_loss
                current_stint += 1
                tyre_age = 0

        pit_traffic_penalty = self.calculate_pit_traffic_penalty(
            circuit_id,
            starting_position,
            len(pit_laps)
        )

        total_race_time += pit_traffic_penalty

        return total_race_time


    def calculate_strategy_time(self, strategy, baseline_pace, total_laps,
                                race_year, starting_position, circuit_id,
                                driver_id):

        if not self.validate_strategy(strategy, total_laps, circuit_id):
            return None

        pit_options = self.calculate_pit_windows(
            strategy, total_laps, circuit_id
        )

        best_time = float("inf")
        best_pit_laps = None

        for pit_laps in pit_options:

            race_time = self.simulate_strategy(
                strategy,
                pit_laps,
                baseline_pace,
                total_laps,
                race_year,
                starting_position,
                circuit_id,
                driver_id
            )

            if race_time < best_time:
                best_time = race_time
                best_pit_laps = pit_laps

        if best_pit_laps is None:
            return None

        return {
            "tyre_sequence": strategy,
            "number_of_stops": len(best_pit_laps),
            "pit_laps": best_pit_laps,
            "estimated_race_time": best_time,
            "simulations": len(pit_options)
        }


    

    def select_best_strategy(self, driver_id, circuit_id, starting_position):

        driver = self.databasemanager.get_driver_by_id(driver_id)

        if driver is None:
            raise ValueError("Driver not found")

        team = driver[2]

        race = self.databasemanager.get_race_by_circuit(circuit_id)

        if race is None:
            raise ValueError("2026 race not found for this circuit")

        total_laps = race[4]
        race_year = race[3]

        baseline_pace = self.get_baseline_pace(
            driver_id, team, circuit_id
        )

        strategies = self.generate_strategy_options()

        best_strategy = None
        all_results = []
        total_simulations = 0

        for strategy in strategies:

            result = self.calculate_strategy_time(
                strategy,
                baseline_pace,
                total_laps,
                race_year,
                starting_position,
                circuit_id,
                driver_id
            )

            if result is None:
                continue
            total_simulations += result["simulations"]

            all_results.append(result)

            if (
                best_strategy is None
                or result["estimated_race_time"]
                < best_strategy["estimated_race_time"]
            ):
                best_strategy = result

        return {
            "best_strategy": best_strategy,
            "all_strategies": all_results,
            "total_simulations": total_simulations
        }






database = DatabaseManager()
database.connect()

driver_name = input("Enter driver name: ").strip()
starting_position = int(input("Enter starting position: "))
circuit_name = input("Enter circuit or country: ").strip()

driver = database.get_driver(driver_name)
circuit = database.get_circuit_by_name(circuit_name)

if driver is None:
    print("Driver not found.")

elif circuit is None:
    print("Circuit not found.")

elif starting_position < 1 or starting_position > 22:
    print("Invalid starting position.")

else:
    engine = StrategyEngine(database)

    result = engine.select_best_strategy(
        driver_id=driver[0],
        circuit_id=circuit[0],
        starting_position=starting_position
    )

    best = result["best_strategy"]

    if best:
        print()
        print("Driver:", driver[1])
        print("Circuit:", circuit[1])
        print("Starting position:", starting_position)
        print("Tyre strategy:", " → ".join(best["tyre_sequence"]))
        print("Number of pit stops:", best["number_of_stops"])
        print("Pit laps:", best["pit_laps"])
        print("Estimated race time:", round(best["estimated_race_time"], 2), "seconds")
        print("Total simulations:", result["total_simulations"])

        one_stop = None
        two_stop = None

        for strategy in result["all_strategies"]:

            if strategy["number_of_stops"] == 1:
                if one_stop is None or strategy["estimated_race_time"] < one_stop["estimated_race_time"]:
                    one_stop = strategy

            elif strategy["number_of_stops"] == 2:
                if two_stop is None or strategy["estimated_race_time"] < two_stop["estimated_race_time"]:
                    two_stop = strategy

        print("\n--- STRATEGY COMPARISON ---")

        if one_stop:
            print("Best one-stop:", " → ".join(one_stop["tyre_sequence"]))
            print("Pit laps:", one_stop["pit_laps"])
            print("Race time:", round(one_stop["estimated_race_time"], 2), "seconds")
        else:
            print("No valid one-stop strategy found.")

        if two_stop:
            print("\nBest two-stop:", " → ".join(two_stop["tyre_sequence"]))
            print("Pit laps:", two_stop["pit_laps"])
            print("Race time:", round(two_stop["estimated_race_time"], 2), "seconds")
        else:
            print("No valid two-stop strategy found.")

database.disconnect()





# 1. Driver performance
# - Historical average lap time: Uses the driver's combined 2025–2026 average at that circuit.
# - Team performance: Uses the team's average lap time if driver history is unavailable.
# - Circuit average: Used as a fallback if neither historical average is available.

# 2. Tyre performance
# - Tyre compound: Soft, Medium, and Hard have different pace characteristics.
# - Tyre lifespan: Each compound has a maximum number of laps it can complete.
# - Tyre degradation: Tyres become slower as they wear down.
# - Circuit tyre wear: Adjusts tyre lifespan depending on whether the circuit has low, medium, or high tyre wear.
# - Tyre age: Tracks how many laps have been completed on the current set.

# 3. Fuel consumption
# - Starting fuel weight: Determined by the race year.
# - Fuel burned per lap: The car gradually becomes lighter.
# - Lap-time adjustment: Accounts for how fuel weight affects pace throughout the race.

# 4. Traffic and overtaking
# - Starting position: Drivers starting further back receive a larger traffic penalty.
# - Overtaking difficulty: Tracks where overtaking is difficult increase that penalty.
# - Historical positions gained: Uses the driver's average starting and finishing positions to adjust the traffic penalty.
# - Early-race traffic: Your current model applies this penalty during the first 10 laps.

# 5. Pit-stop strategy
# - Number of pit stops: Compares one-stop and two-stop strategies.
# - Pit-stop time loss: Adds the circuit's pit-stop penalty each time the driver pits.
# - Pit-stop timing: Tests every pit-stop combination permitted by the tyre lifespan limits.
# - Tyre changes: Resets tyre age whenever a new compound is fitted.
# - F1 tyre rules: Requires at least two different dry tyre compounds.
