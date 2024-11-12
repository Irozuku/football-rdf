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
        self.FOOTBALL = Namespace("http://example.org/FOOTBALL/")
        self.WD = Namespace("http://www.wikidata.org/entity/")

        # Bind namespaces
        self.rdf_graph.bind("FOOTBALL", self.FOOTBALL)
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

    def link_players_to_wikidata(self):
        for player in self.rdf_graph.subjects(RDF.type, self.FOOTBALL.Player):
            player_name = str(player).split("/")[-1].replace("_", " ")
            wikidata_url = f"https://www.wikidata.org/w/api.php?action=wbsearchentities&search={player_name}&language=en&format=json&type=item"
            response = requests.get(wikidata_url)
            data = response.json()
            if data['search']:
                wikidata_id = data['search'][0]['id']
                wikidata_uri = URIRef(f"http://www.wikidata.org/entity/{wikidata_id}")
                self.rdf_graph.add((player, OWL.sameAs, wikidata_uri))

    def load_all_data(self):
        base_path = "./datasets"
        # Premier league players data
        self.add_player_data(os.path.join(base_path, "Premleg_23_24/player_total_scoring_attempts.csv"), 'scoring', 'PremierLeague')
        self.add_player_data(os.path.join(base_path, "Premleg_23_24/player_top_scorers.csv"), 'goals', 'PremierLeague')
        self.add_player_data(os.path.join(base_path, "Premleg_23_24/player_total_assists_in_attack.csv"), 'chances', 'PremierLeague')
        self.add_player_data(os.path.join(base_path, "Premleg_23_24/player_top_assists.csv"), 'assists', 'PremierLeague')

        # La Liga players data
        self.add_player_data(os.path.join(base_path, "laliga2023_34/player_total_scoring_attempts.csv"), 'scoring', 'LaLiga')
        self.add_player_data(os.path.join(base_path, "laliga2023_34/player_top_scorers.csv"), 'goals', 'LaLiga')
        self.add_player_data(os.path.join(base_path, "laliga2023_34/player_total_assists_in_attack.csv"), 'chances', 'LaLiga')
        self.add_player_data(os.path.join(base_path, "laliga2023_34/player_top_assists.csv"), 'assists', 'LaLiga')
        
        # Serie A players data
        self.add_player_data(os.path.join(base_path, "SerieA23_24/player_total_scoring_attempts.csv"), 'scoring', 'SerieA')
        self.add_player_data(os.path.join(base_path, "SerieA23_24/player_top_scorers.csv"), 'goals', 'SerieA')
        self.add_player_data(os.path.join(base_path, "SerieA23_24/player_total_assists_in_attack.csv"), 'chances', 'SerieA')
        self.add_player_data(os.path.join(base_path, "SerieA23_24/player_top_assists.csv"), 'assists', 'SerieA')

        # Link players to Wikidata
        # self.link_players_to_wikidata()

    def save_ontology(self, destination="football_ontology.ttl"):
        self.rdf_graph.serialize(destination=destination, format="turtle")



if __name__ == "__main__":
    graph = FootballGraph()
    graph.load_all_data()
    graph.save_ontology()
    print("Football ontology saved to football_ontology.ttl")