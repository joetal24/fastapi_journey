from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

load_dotenv()

# ── Neo4j Connection ───────────────────────────────────────────────
driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
)

def verify_connectivity():
    """Test Neo4j connection."""
    driver.verify_connectivity()
    print("Neo4j connected successfully")

# ── Fraud Detection Functions ──────────────────────────────────────
def register_ownership(plot_id: str, owner_name: str, 
                       national_id: str, amount: float, date: str):
    """
    Register a new land ownership in the graph.
    Called every time a new verification comes in.
    """
    with driver.session() as session:
        session.run("""
            MERGE (p:Person {national_id: $national_id})
            SET p.name = $owner_name
            MERGE (plot:Plot {plot_id: $plot_id})
            MERGE (p)-[:OWNS {since: $date, amount: $amount}]->(plot)
        """, national_id=national_id, owner_name=owner_name,
             plot_id=plot_id, amount=amount, date=date)


def register_transfer(from_national_id: str, to_national_id: str,
                      to_name: str, plot_id: str, 
                      amount: float, date: str):
    """
    Register a title transfer between two people.
    Then automatically checks for circular fraud.
    """
    with driver.session() as session:
        # Record the transfer
        session.run("""
            MATCH (from:Person {national_id: $from_id})
            MERGE (to:Person {national_id: $to_id})
            SET to.name = $to_name
            MERGE (plot:Plot {plot_id: $plot_id})
            CREATE (from)-[:TRANSFERRED_TO {
                date: $date, 
                amount: $amount
            }]->(to)
            MERGE (to)-[:OWNS {since: $date}]->(plot)
        """, from_id=from_national_id, to_id=to_national_id,
             to_name=to_name, plot_id=plot_id,
             amount=amount, date=date)

        # Immediately check for fraud
        return check_circular_fraud(from_national_id)


def check_circular_fraud(national_id: str) -> dict:
    """
    Check if a person is involved in any circular 
    ownership chain — the core fraud detection query.
    """
    with driver.session() as session:
        result = session.run("""
            MATCH path = (a:Person {national_id: $national_id})
                         -[:TRANSFERRED_TO*]->(a)
            RETURN 
                a.name as suspicious_person,
                a.national_id as national_id,
                length(path) as chain_length,
                [r in relationships(path) | r.date] as transfer_dates,
                [r in relationships(path) | r.amount] as amounts
            LIMIT 1
        """, national_id=national_id)

        record = result.single()

        if record:
            amounts = record["amounts"]
            # Check if amounts are inflating — fraud signal
            inflating = all(
                amounts[i] < amounts[i+1] 
                for i in range(len(amounts)-1)
                if amounts[i] and amounts[i+1]
            )
            return {
                "fraud_detected": True,
                "suspicious_person": record["suspicious_person"],
                "national_id": record["national_id"],
                "chain_length": record["chain_length"],
                "transfer_dates": record["transfer_dates"],
                "amounts": record["amounts"],
                "inflating_values": inflating,
                "risk_level": "HIGH" if inflating else "MEDIUM"
            }

        return {"fraud_detected": False}
        