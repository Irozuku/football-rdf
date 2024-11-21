from SPARQLWrapper import SPARQLWrapper, JSON
import json
import pandas as pd
from rdflib import Graph, Namespace, Literal, URIRef, BNode
from rdflib.namespace import RDF, RDFS, OWL, XSD
import os
import requests

class FootballGraph:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FootballGraph, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.rdf_graph = Graph()
        self.FOOTBALL = Namespace("http://example.org/football/")
        self.WD = Namespace("http://www.wikidata.org/entity/")

        # Bind namespaces
        self.rdf_graph.bind("fb", self.FOOTBALL)
        self.rdf_graph.bind("wd", self.WD)
        self.rdf_graph.bind("owl", OWL)

        # Define classes
        self.rdf_graph.add((self.FOOTBALL.Player, RDF.type, OWL.Class))
        self.rdf_graph.add((self.FOOTBALL.Team, RDF.type, OWL.Class))
        self.rdf_graph.add((self.FOOTBALL.Country, RDF.type, OWL.Class))
        self.rdf_graph.add((self.FOOTBALL.League, RDF.type, OWL.Class))
        self.rdf_graph.add((self.FOOTBALL.PlayerStats, RDF.type, OWL.Class))

        # Define properties
        self.rdf_graph.add((self.FOOTBALL.playsFor, RDF.type, OWL.ObjectProperty))
        self.rdf_graph.add((self.FOOTBALL.nationality, RDF.type, OWL.ObjectProperty))
        self.rdf_graph.add((self.FOOTBALL.hasStats, RDF.type, OWL.ObjectProperty))
        self.rdf_graph.add((self.FOOTBALL.inLeague, RDF.type, OWL.ObjectProperty))
        self.rdf_graph.add((self.FOOTBALL.inTeam, RDF.type, OWL.ObjectProperty))
        self.rdf_graph.add((self.FOOTBALL.inSeason, RDF.type, OWL.DatatypeProperty))
        self.rdf_graph.add((self.FOOTBALL.shotsPerNinety, RDF.type, OWL.DatatypeProperty))
        self.rdf_graph.add((self.FOOTBALL.shotConversionRate, RDF.type, OWL.DatatypeProperty))
        self.rdf_graph.add((self.FOOTBALL.minutes, RDF.type, OWL.DatatypeProperty))
        self.rdf_graph.add((self.FOOTBALL.matches, RDF.type, OWL.DatatypeProperty))
        self.rdf_graph.add((self.FOOTBALL.goals, RDF.type, OWL.DatatypeProperty))
        self.rdf_graph.add((self.FOOTBALL.penalties, RDF.type, OWL.DatatypeProperty))
        self.rdf_graph.add((self.FOOTBALL.chancesCreated, RDF.type, OWL.DatatypeProperty))
        self.rdf_graph.add((self.FOOTBALL.chancesCreatedPerNinety, RDF.type, OWL.DatatypeProperty))
        self.rdf_graph.add((self.FOOTBALL.assists, RDF.type, OWL.DatatypeProperty))
        self.rdf_graph.add((self.FOOTBALL.secondaryAssists, RDF.type, OWL.DatatypeProperty))
        
        # TeamStats
        self.rdf_graph.add((self.FOOTBALL.bigChances, RDF.type, OWL.DatatypeProperty))
        self.rdf_graph.add((self.FOOTBALL.goalsPerMatch, RDF.type, OWL.DatatypeProperty))
        self.rdf_graph.add((self.FOOTBALL.savesPerMatch, RDF.type, OWL.DatatypeProperty))
        self.rdf_graph.add((self.FOOTBALL.totalSaves, RDF.type, OWL.DatatypeProperty))
        self.rdf_graph.add((self.FOOTBALL.accuratePassesPerMatch, RDF.type, OWL.DatatypeProperty))
        self.rdf_graph.add((self.FOOTBALL.passSuccessPercentage, RDF.type, OWL.DatatypeProperty))

        # Connect with Wikidata
        self.rdf_graph.add((self.FOOTBALL.Player, OWL.equivalentClass, self.WD.Q937857))  # Football player
        self.rdf_graph.add((self.FOOTBALL.Team, OWL.equivalentClass, self.WD.Q476028))  # Association football club
        self.rdf_graph.add((self.FOOTBALL.Country, OWL.equivalentClass, self.WD.Q6256))  # Country
        self.rdf_graph.add((self.FOOTBALL.League, OWL.equivalentClass, self.WD.Q15089))  # Sports league
        self.rdf_graph.add((self.FOOTBALL.playsFor, OWL.equivalentProperty, self.WD.P54))  # Member of sports team
        self.rdf_graph.add((self.FOOTBALL.nationality, OWL.equivalentProperty, self.WD.P27))  # Country of citizenship
        self.rdf_graph.add((self.FOOTBALL.goals, OWL.equivalentProperty, self.WD.P1351))  # Number of points/goals/set scored

    def safe_literal(self, value, datatype):
        """Safely create a Literal, converting floats to integers when necessary."""
        if pd.isna(value):
            return None
        if datatype == XSD.integer:
            try:
                return Literal(int(float(value)), datatype=XSD.integer)
            except ValueError:
                return Literal(0, datatype=XSD.integer)  # Default to 0 if conversion fails
        elif datatype == XSD.decimal:
            try:
                return Literal(float(value), datatype=XSD.decimal)
            except ValueError:
                return Literal(0.0, datatype=XSD.decimal)  # Default to 0.0 if conversion fails
        else:
            return Literal(value, datatype=datatype)

    def add_player_data(self, file_path, file_type, league):
        df = pd.read_csv(file_path)
        
        for _, row in df.iterrows():
            player_uri = URIRef(self.FOOTBALL[row['Player'].replace(" ", "_")])
            self.rdf_graph.add((player_uri, RDF.type, self.FOOTBALL.Player))
            
            team_uri = URIRef(self.FOOTBALL[row['Team'].replace(" ", "_")])
            self.rdf_graph.add((team_uri, RDF.type, self.FOOTBALL.Team))
            self.rdf_graph.add((player_uri, self.FOOTBALL.playsFor, team_uri))
            
            country_uri = URIRef(self.FOOTBALL[row['Country']])
            self.rdf_graph.add((country_uri, RDF.type, self.FOOTBALL.Country))
            self.rdf_graph.add((player_uri, self.FOOTBALL.nationality, country_uri))
            
            league_uri = URIRef(self.FOOTBALL[league])
            self.rdf_graph.add((league_uri, RDF.type, self.FOOTBALL.League))

            # Create a new PlayerStats instance for this player in this league
            stats_uri = BNode()
            self.rdf_graph.add((stats_uri, RDF.type, self.FOOTBALL.PlayerStats))
            self.rdf_graph.add((player_uri, self.FOOTBALL.hasStats, stats_uri))
            self.rdf_graph.add((stats_uri, self.FOOTBALL.inLeague, league_uri))
            self.rdf_graph.add((stats_uri, self.FOOTBALL.inTeam, team_uri))
            self.rdf_graph.add((stats_uri, self.FOOTBALL.inSeason, Literal("2023/24", datatype=XSD.string)))
            
            # Add minutes and matches data if available
            if 'Minutes' in df.columns:
                minutes_literal = self.safe_literal(row['Minutes'], datatype=XSD.integer)
                if minutes_literal:
                    self.rdf_graph.add((stats_uri, self.FOOTBALL.minutes, minutes_literal))
            if 'Matches' in df.columns:
                matches_literal = self.safe_literal(row['Matches'], datatype=XSD.integer)
                if matches_literal:
                    self.rdf_graph.add((stats_uri, self.FOOTBALL.matches, matches_literal))
            
            # Add specific stats based on file_type
            if file_type == 'scoring':
                if 'Shots per 90' in df.columns:
                    shots_per_90_literal = self.safe_literal(row['Shots per 90'], datatype=XSD.decimal)
                    if shots_per_90_literal:
                        self.rdf_graph.add((stats_uri, self.FOOTBALL.shotsPerNinety, shots_per_90_literal))
                if 'Shot Conversion Rate (%)' in df.columns:
                    shot_conversion_rate_literal = self.safe_literal(row['Shot Conversion Rate (%)'], datatype=XSD.decimal)
                    if shot_conversion_rate_literal:
                        self.rdf_graph.add((stats_uri, self.FOOTBALL.shotConversionRate, shot_conversion_rate_literal))
            elif file_type == 'goals':
                if 'Goals' in df.columns:
                    goals_literal = self.safe_literal(row['Goals'], datatype=XSD.integer)
                    if goals_literal:
                        self.rdf_graph.add((stats_uri, self.FOOTBALL.goals, goals_literal))
                if 'Penalties' in df.columns:
                    penalties_literal = self.safe_literal(row['Penalties'], datatype=XSD.integer)
                    if penalties_literal:
                        self.rdf_graph.add((stats_uri, self.FOOTBALL.penalties, penalties_literal))
            elif file_type == 'chances':
                if 'Chances Created' in df.columns:
                    chances_created_literal = self.safe_literal(row['Chances Created'], datatype=XSD.integer)
                    if chances_created_literal:
                        self.rdf_graph.add((stats_uri, self.FOOTBALL.chancesCreated, chances_created_literal))
                if 'Chances Created per 90' in df.columns:
                    chances_created_per_90_literal = self.safe_literal(row['Chances Created per 90'], datatype=XSD.decimal)
                    if chances_created_per_90_literal:
                        self.rdf_graph.add((stats_uri, self.FOOTBALL.chancesCreatedPerNinety, chances_created_per_90_literal))
            elif file_type == 'assists':
                if 'Assists' in df.columns:
                    assists_literal = self.safe_literal(row['Assists'], datatype=XSD.integer)
                    if assists_literal:
                        self.rdf_graph.add((stats_uri, self.FOOTBALL.assists, assists_literal))
                if 'Secondary Assists' in df.columns:
                    secondary_assists_literal = self.safe_literal(row['Secondary Assists'], datatype=XSD.decimal)
                    if secondary_assists_literal:
                        self.rdf_graph.add((stats_uri, self.FOOTBALL.secondaryAssists, secondary_assists_literal))

    def add_team_data(self, file_path, data_type, league):
        df = pd.read_csv(file_path)
        
        for _, row in df.iterrows():
            team_uri = URIRef(self.FOOTBALL[row['Team'].replace(" ", "_")])
            self.rdf_graph.add((team_uri, RDF.type, self.FOOTBALL.Team))
            
            country_uri = URIRef(self.FOOTBALL[row['Country']])
            self.rdf_graph.add((country_uri, RDF.type, self.FOOTBALL.Country))
            self.rdf_graph.add((team_uri, self.FOOTBALL.nationality, country_uri))
            
            league_uri = URIRef(self.FOOTBALL[league])
            self.rdf_graph.add((league_uri, RDF.type, self.FOOTBALL.League))
            self.rdf_graph.add((team_uri, self.FOOTBALL.inLeague, league_uri))
            
            # Create a new TeamStats instance for this team
            stats_uri = BNode()
            self.rdf_graph.add((stats_uri, RDF.type, self.FOOTBALL.TeamStats))
            self.rdf_graph.add((team_uri, self.FOOTBALL.hasTeamStats, stats_uri))
            
            # Add matches played
            matches_literal = self.safe_literal(row['Matches'], datatype=XSD.integer)
            if matches_literal:
                self.rdf_graph.add((stats_uri, self.FOOTBALL.gamesPlayed, matches_literal))
            
            # Add specific stats based on data_type
            if data_type == 'big_chance':
                big_chances_literal = self.safe_literal(row['Big Chances'], datatype=XSD.integer)
                goals_literal = self.safe_literal(row['Goals'], datatype=XSD.integer)
                if big_chances_literal:
                    self.rdf_graph.add((stats_uri, self.FOOTBALL.bigChances, big_chances_literal))
                if goals_literal:
                    self.rdf_graph.add((stats_uri, self.FOOTBALL.goalsFor, goals_literal))
            elif data_type == 'goals_per_match':
                goals_per_match_literal = self.safe_literal(row['Goals per Match'], datatype=XSD.decimal)
                total_goals_literal = self.safe_literal(row['Total Goals Scored'], datatype=XSD.integer)
                if goals_per_match_literal:
                    self.rdf_graph.add((stats_uri, self.FOOTBALL.goalsPerMatch, goals_per_match_literal))
                if total_goals_literal:
                    self.rdf_graph.add((stats_uri, self.FOOTBALL.goalsFor, total_goals_literal))
            elif data_type == 'saves':
                saves_per_match_literal = self.safe_literal(row['Saves per Match'], datatype=XSD.decimal)
                total_saves_literal = self.safe_literal(row['Total Saves'], datatype=XSD.integer)
                if saves_per_match_literal:
                    self.rdf_graph.add((stats_uri, self.FOOTBALL.savesPerMatch, saves_per_match_literal))
                if total_saves_literal:
                    self.rdf_graph.add((stats_uri, self.FOOTBALL.totalSaves, total_saves_literal))
            elif data_type == 'accurate_pass':
                accurate_passes_literal = self.safe_literal(row['Accurate Passes per Match'], datatype=XSD.decimal)
                pass_success_literal = self.safe_literal(row['Pass Success (%)'], datatype=XSD.decimal)
                if accurate_passes_literal:
                    self.rdf_graph.add((stats_uri, self.FOOTBALL.accuratePassesPerMatch, accurate_passes_literal))
                if pass_success_literal:
                    self.rdf_graph.add((stats_uri, self.FOOTBALL.passSuccessPercentage, pass_success_literal))

    def country_iso_to_name(self, country_iso_code):
        with open('./iso_to_country.json', 'r') as file:
            json_data: json = json.load(file)
            try:
                return json_data[country_iso_code]
            except KeyError:
                return None
        
    def link_country_to_wikidata(self):
        endpoint_url = "https://query.wikidata.org/sparql"
        
        base_query = """
        ASK
        WHERE {
            ?country wdt:P31 wd:Q6256 . # country
            VALUES ?country { %s }
        }
        """
            
        for country in self.rdf_graph.subjects(RDF.type, self.FOOTBALL.Country):
            country_iso_code = str(country).split("/")[-1].replace("_", " ")
            country_name = self.country_iso_to_name(country_iso_code)
            if not country_name:
                print(f"Couldn't find the country name for {country_iso_code}")
                continue
            
            # We use the search engine of wikidata
            wikidata_url = f"https://www.wikidata.org/w/api.php?action=wbsearchentities&search={country_name}&language=en&format=json&type=item"
            response = requests.get(wikidata_url)
            data = response.json()
            wikidata_results = data['search']
            
            # We iterate over the results and use sparql to query checking if they are countries
            for result in wikidata_results:
                wikidata_id = result['id']
                sparql_values = "wd:" + wikidata_id
                
                query = base_query % sparql_values
                
                sparql = SPARQLWrapper(endpoint_url)
                sparql.setQuery(query)
                sparql.setReturnFormat(JSON)
                
                try:
                    results = sparql.query().convert()
                    if results["boolean"]:
                        wikidata_uri = URIRef(f"http://www.wikidata.org/entity/{result['id']}")
                        self.rdf_graph.add((country, OWL.sameAs, wikidata_uri))
                        break
                except Exception as e:
                    print(f"Fail: Couldn't execute the query for {country_name}, {wikidata_id}")

    def link_leagues_to_wikidata(self):
        wikidata_leagues = {
            "PremierLeague": "http://www.wikidata.org/entity/Q9448",
            "LaLiga": "http://www.wikidata.org/entity/Q324867",
            "SerieA": "http://www.wikidata.org/entity/Q15804"
        }
        
        for league in self.rdf_graph.subjects(RDF.type, self.FOOTBALL.League):
            league_name = str(league).split("/")[-1].replace("_", " ")
            wikidata_uri = URIRef(wikidata_leagues[league_name])
            self.rdf_graph.add((league, OWL.sameAs, wikidata_uri))
        
    def link_players_to_wikidata(self):
        endpoint_url = "https://query.wikidata.org/sparql"
        
        base_query = """
        ASK
        WHERE {
            ?player wdt:P106 wd:Q937857 . # football player
            ?player wdt:P19|wdt:P27 ?country . # country
            VALUES ( ?player ?country ) { %s }
        }
        """
        
        for player in self.rdf_graph.subjects(RDF.type, self.FOOTBALL.Player):
            player_name = str(player).split("/")[-1].replace("_", " ")
            # We use the search engine of wikidata  
            wikidata_url = f"https://www.wikidata.org/w/api.php?action=wbsearchentities&search={player_name}&language=en&format=json&type=item"
            response = requests.get(wikidata_url)
            data = response.json()
            wikidata_results = data['search']
            
            country_uri = self.rdf_graph.value(player, self.FOOTBALL.nationality)
            wikidata_country = self.rdf_graph.value(country_uri, OWL.sameAs)
            country_wikidata_id = "wd:" + str(wikidata_country).split("/")[-1]
            
            # We iterate over the results and use sparql to query checking if they are players
            for result in wikidata_results:
                player_wikidata_id = "wd:" + result['id']
                
                if not country_uri:
                    base_query = """
                    ASK
                    WHERE {
                        ?player wdt:P106 wd:Q937857 . # football player
                        VALUES ?player { %s }
                    }
                    """
                    sparql_values = player_wikidata_id
                else:
                    sparql_values = f"({player_wikidata_id} {country_wikidata_id})"
                    
                query = base_query % sparql_values
                
                sparql = SPARQLWrapper(endpoint_url)
                sparql.setQuery(query)
                sparql.setReturnFormat(JSON)
                
                try:
                    results = sparql.query().convert()
                    if results["boolean"]:
                        wikidata_uri = URIRef(f"http://www.wikidata.org/entity/{result['id']}")
                        self.rdf_graph.add((player, OWL.sameAs, wikidata_uri))
                        break
                except Exception as e:
                    print(f"Fail: Couldn't execute the query for {player_name}, {player_wikidata_id}")
   
    def link_teams_to_wikidata(self):
        endpoint_url = "https://query.wikidata.org/sparql"
        
        base_query = """
        ASK
        WHERE {
            ?team wdt:P31 wd:Q476028 . # team
            VALUES ?team { %s }
        }
        """
        
        for team in self.rdf_graph.subjects(RDF.type, self.FOOTBALL.Team):
            team_name = str(team).split("/")[-1].replace("_", " ")
            # We use the search engine of wikidata
            wikidata_url = f"https://www.wikidata.org/w/api.php?action=wbsearchentities&search={team_name}&language=en&format=json&type=item"
            response = requests.get(wikidata_url)
            data = response.json()
            wikidata_results = data['search']
            
            # We iterate over the results and use sparql to query checking if they are teams
            for result in wikidata_results:
                wikidata_id = result['id']
                sparql_values = "wd:" + wikidata_id
                query = base_query % sparql_values
                
                sparql = SPARQLWrapper(endpoint_url)
                sparql.setQuery(query)
                sparql.setReturnFormat(JSON)
                
                try:
                    results = sparql.query().convert()
                    if results["boolean"]:
                        wikidata_uri = URIRef(f"http://www.wikidata.org/entity/{wikidata_id}")
                        self.rdf_graph.add((team, OWL.sameAs, wikidata_uri))
                        break
                except Exception as e:
                    print(f"Fail: Couldn't execute the query for {team_name}, {wikidata_id}")

    def load_all_data(self):
        base_path = "./datasets"
        # Premier league data
        # Players data
        self.add_player_data(os.path.join(base_path, "Premleg_23_24/player_total_scoring_attempts.csv"), 'scoring', 'PremierLeague')
        self.add_player_data(os.path.join(base_path, "Premleg_23_24/player_top_scorers.csv"), 'goals', 'PremierLeague')
        self.add_player_data(os.path.join(base_path, "Premleg_23_24/player_total_assists_in_attack.csv"), 'chances', 'PremierLeague')
        self.add_player_data(os.path.join(base_path, "Premleg_23_24/player_top_assists.csv"), 'assists', 'PremierLeague')
        
        # Teams data
        self.add_team_data(os.path.join(base_path, "Premleg_23_24/big_chance_team.csv"), 'big_chance', 'PremierLeague')
        self.add_team_data(os.path.join(base_path, "Premleg_23_24/team_goals_per_match.csv"), 'goals_per_match', 'PremierLeague')
        self.add_team_data(os.path.join(base_path, "Premleg_23_24/saves_team.csv"), 'saves', 'PremierLeague')
        self.add_team_data(os.path.join(base_path, "Premleg_23_24/accurate_pass_team.csv"), 'accurate_pass', 'PremierLeague')

        # La Liga data
        # Players data
        self.add_player_data(os.path.join(base_path, "laliga2023_34/player_total_scoring_attempts.csv"), 'scoring', 'LaLiga')
        self.add_player_data(os.path.join(base_path, "laliga2023_34/player_top_scorers.csv"), 'goals', 'LaLiga')
        self.add_player_data(os.path.join(base_path, "laliga2023_34/player_total_assists_in_attack.csv"), 'chances', 'LaLiga')
        self.add_player_data(os.path.join(base_path, "laliga2023_34/player_top_assists.csv"), 'assists', 'LaLiga')
        
        # Teams data
        self.add_team_data(os.path.join(base_path, "laliga2023_34/big_chance_team.csv"), 'big_chance', 'LaLiga')
        self.add_team_data(os.path.join(base_path, "laliga2023_34/team_goals_per_match.csv"), 'goals_per_match', 'LaLiga')
        self.add_team_data(os.path.join(base_path, "laliga2023_34/saves_team.csv"), 'saves', 'LaLiga')
        self.add_team_data(os.path.join(base_path, "laliga2023_34/accurate_pass_team.csv"), 'accurate_pass', 'LaLiga')
        
        # Serie A data
        # Players data
        self.add_player_data(os.path.join(base_path, "SerieA23_24/player_total_scoring_attempts.csv"), 'scoring', 'SerieA')
        self.add_player_data(os.path.join(base_path, "SerieA23_24/player_top_scorers.csv"), 'goals', 'SerieA')
        self.add_player_data(os.path.join(base_path, "SerieA23_24/player_total_assists_in_attack.csv"), 'chances', 'SerieA')
        self.add_player_data(os.path.join(base_path, "SerieA23_24/player_top_assists.csv"), 'assists', 'SerieA')
        
        # Teams data
        self.add_team_data(os.path.join(base_path, "SerieA23_24/big_chance_team.csv"), 'big_chance', 'SerieA')
        self.add_team_data(os.path.join(base_path, "SerieA23_24/team_goals_per_match.csv"), 'goals_per_match', 'SerieA')
        self.add_team_data(os.path.join(base_path, "SerieA23_24/saves_team.csv"), 'saves', 'SerieA')
        self.add_team_data(os.path.join(base_path, "SerieA23_24/accurate_pass_team.csv"), 'accurate_pass', 'SerieA')
    
    def link_to_wikidata(self):
        self.link_country_to_wikidata()
        self.link_leagues_to_wikidata()
        self.link_teams_to_wikidata()
        self.link_players_to_wikidata()

    def save_ontology(self, destination="football_ontology.ttl"):
        self.rdf_graph.serialize(destination=destination, format="turtle")



if __name__ == "__main__":
    graph = FootballGraph()
    graph.load_all_data()
    graph.link_to_wikidata()
    graph.save_ontology()
    print("Football ontology saved to football_ontology.ttl")