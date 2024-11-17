from rdflib import Graph
from rdflib.plugins.sparql import prepareQuery

# Load the RDF graph
g = Graph()
g.parse("football_ontology.ttl", format="turtle")


print("Top 10 players by total goals in each league:")
print()

# Prepare and execute the query
query = prepareQuery("""
PREFIX fb: <http://example.org/football/>

SELECT ?playerName ?leagueName (SUM(?goals) AS ?totalGoals)
WHERE {
  ?player a fb:Player ;
          fb:hasStats ?stats ;
          fb:playsFor ?team .
  ?stats fb:inLeague ?league ;
         fb:goals ?goals .
  BIND(STRAFTER(STR(?league), "http://example.org/football/") AS ?leagueName)
  BIND(STRAFTER(STR(?player), "http://example.org/football/") AS ?playerName)
}
GROUP BY ?playerName ?leagueName
ORDER BY DESC(?totalGoals)
LIMIT 10
""")

results = g.query(query)

# Print the results
for row in results:
    print(f"Player: {row.playerName}, League: {row.leagueName}, Total Goals: {row.totalGoals}")


print()
print("--------------------------------------------------------------------------------")
print()

print("Top 10 players with the highest shot conversion rate (minimum 5 goals):")
print()

# Prepare and execute the query
query = prepareQuery("""
PREFIX fb: <http://example.org/football/>

SELECT ?playerName ?leagueName ?goals ?conversionRate
WHERE {
  ?player a fb:Player ;
          fb:hasStats ?statsGoals, ?statsShots .
  ?statsGoals fb:inLeague ?league ;
              fb:goals ?goals .
  ?statsShots fb:inLeague ?league ;
              fb:shotConversionRate ?conversionRate .
  FILTER (?goals >= 5)
  BIND(STRAFTER(STR(?league), "http://example.org/football/") AS ?leagueName)
  BIND(STRAFTER(STR(?player), "http://example.org/football/") AS ?playerName)
}
ORDER BY DESC(?conversionRate)
LIMIT 10
""")

results = g.query(query)

# Print the results
for row in results:
    print(f"Player: {row.playerName}, League: {row.leagueName}, Total Goals: {row.conversionRate}")


print() 
print("--------------------------------------------------------------------------------")
print()


print("Players who have created the most chances but have not scored any goals:")
print()

# Prepare and execute the query
query = prepareQuery("""
PREFIX fb: <http://example.org/football/>

SELECT ?playerName ?leagueName ?chancesCreated
WHERE {
  ?player a fb:Player ;
          fb:hasStats ?statsChances, ?statsGoals .
  ?statsChances fb:inLeague ?league ;
                fb:chancesCreated ?chancesCreated .
  ?statsGoals fb:inLeague ?league ;
              fb:goals ?goals .
  FILTER (?goals = 0)
  BIND(STRAFTER(STR(?league), "http://example.org/football/") AS ?leagueName)
  BIND(STRAFTER(STR(?player), "http://example.org/football/") AS ?playerName)
}
ORDER BY DESC(?chancesCreated)
LIMIT 10
""")

results = g.query(query)

# Print the results
for row in results:
    print(f"Player: {row.playerName}, League: {row.leagueName}, Chances Created: {row.chancesCreated}")
    
    
print()
print("--------------------------------------------------------------------------------")
print()


print("Compare the average shots per 90 minutes of all leagues:")
print()

# Prepare and execute the query
query = prepareQuery("""
PREFIX fb: <http://example.org/football/>

SELECT ?leagueName (AVG(?shotsPerNinety) AS ?avgShotsPerNinety)
WHERE {
  ?player fb:hasStats ?stats .
  ?stats fb:inLeague ?league ;
         fb:shotsPerNinety ?shotsPerNinety .
  BIND(STRAFTER(STR(?league), "http://example.org/football/") AS ?leagueName)
}
GROUP BY ?leagueName
ORDER BY DESC(?avgShotsPerNinety)
""")

results = g.query(query)

# Print the results
for row in results:
    print(f"League: {row.leagueName}, Average shots per ninety: {row.avgShotsPerNinety}")
    

print()
print("--------------------------------------------------------------------------------")
print()


print("Players who have score stats in both Premier League and La Liga:")
print()

# Prepare and execute the query
query = prepareQuery("""
PREFIX fb: <http://example.org/football/>

SELECT ?playerName ?premierLeagueGoals ?laLigaGoals
WHERE {
  ?player a fb:Player ;
          fb:hasStats ?statsPL, ?statsLaLiga .

  # Ensure that the Premier League stats contain goals data
  ?statsPL fb:inLeague fb:PremierLeague .
  OPTIONAL { ?statsPL fb:goals ?premierLeagueGoals }
  
  # Ensure that the La Liga stats contain goals data
  ?statsLaLiga fb:inLeague fb:LaLiga .
  OPTIONAL { ?statsLaLiga fb:goals ?laLigaGoals }
  
  # Filter players with goals in both leagues
  FILTER (BOUND(?premierLeagueGoals) && BOUND(?laLigaGoals))
  
  # Extract player name from URI
  BIND(STRAFTER(STR(?player), "http://example.org/football/") AS ?playerName)
}
ORDER BY DESC(?premierLeagueGoals) DESC(?laLigaGoals)
LIMIT 10
""")

results = g.query(query)

# Print the results
for row in results:
    print(f"Player: {row.playerName}, Premier League Goals: {row.premierLeagueGoals}, La Liga Goals: {row.laLigaGoals}")
 

print()
print("--------------------------------------------------------------------------------")   
print()


print("Top scorers in the Premier League:")
print()

# Prepare and execute the query
query = prepareQuery("""
PREFIX fb: <http://example.org/football/>

SELECT ?playerName ?goals
WHERE {
  ?player a fb:Player ;
          fb:hasStats ?stats .
  ?stats fb:inLeague fb:PremierLeague ;
         fb:goals ?goals .
  BIND(STRAFTER(STR(?player), "http://example.org/football/") AS ?playerName)
}
ORDER BY DESC(?goals)
LIMIT 10
""")
results = g.query(query)
for row in results:
    print(f"Player: {row.playerName}, Goals: {row.goals}")    

print()
print("--------------------------------------------------------------------------------")   
print()


print("Players with the highest shot conversion rate in La Liga:")
print()

# Prepare and execute the query
query = prepareQuery("""
PREFIX fb: <http://example.org/football/>

SELECT ?playerName ?conversionRate
WHERE {
  ?player a fb:Player ;
          fb:hasStats ?stats .
  ?stats fb:inLeague fb:LaLiga ;
         fb:shotConversionRate ?conversionRate .
  BIND(STRAFTER(STR(?player), "http://example.org/football/") AS ?playerName)
}
ORDER BY DESC(?conversionRate)
LIMIT 10
""")
results = g.query(query)
for row in results:
    print(f"Player: {row.playerName}, Conversion Rate: {row.conversionRate}")


print()
print("--------------------------------------------------------------------------------")   
print()


print("Top 10 Players and their minutes played in a league:")
print()

# Prepare and execute the query
query = prepareQuery("""
PREFIX fb: <http://example.org/football/>

SELECT DISTINCT ?playerName ?league ?minutes
WHERE {
  ?player a fb:Player ;
          fb:hasStats ?stats .
  ?stats fb:inLeague ?league ;
         fb:minutes ?minutes .
  BIND(STRAFTER(STR(?player), "http://example.org/football/") AS ?playerName)
  BIND(STRAFTER(STR(?league), "http://example.org/football/") AS ?league)
}
ORDER BY DESC(?minutes)
LIMIT 10
""")
results = g.query(query)
for row in results:
    print(f"Player: {row.playerName}, League: {row.league}, Minutes: {row.minutes}")


print()
print("--------------------------------------------------------------------------------")   
print()


print("Players with the most assists in La Liga:")
print()

# Prepare and execute the query
query = prepareQuery("""
PREFIX fb: <http://example.org/football/>

SELECT ?playerName ?assists
WHERE {
  ?player a fb:Player ;
          fb:hasStats ?stats .
  ?stats fb:inLeague fb:LaLiga ;
         fb:assists ?assists .
  BIND(STRAFTER(STR(?player), "http://example.org/football/") AS ?playerName)
}
ORDER BY DESC(?assists)
LIMIT 10
""")
results = g.query(query)
for row in results:
    print(f"Player: {row.playerName}, Assists: {row.assists}")
