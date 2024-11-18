import json
import os
from datetime import datetime

class CharacterRelationshipManager:
    def __init__(self, relationship_file="data/relationships.json"):
        self.relationship_file = relationship_file
        self.relationships = self._load_relationships()

    def _load_relationships(self):
        """Load relationships from a JSON file."""
        if os.path.exists(self.relationship_file):
            with open(self.relationship_file, 'r') as f:
                return json.load(f)
        return {}

    def save_relationships(self):
        """Save relationships to a JSON file."""
        with open(self.relationship_file, 'w') as f:
            json.dump(self.relationships, f, indent=2)

    def update_relationship(self, character_a, character_b, interaction_type):
        """Update the relationship between two characters based on interaction."""
        if character_a not in self.relationships:
            self.relationships[character_a] = {}
        if character_b not in self.relationships[character_a]:
            self.relationships[character_a][character_b] = {
                "relationship_score": 0,
                "last_interaction": None
            }

        # Update relationship score based on interaction type
        if interaction_type == "positive":
            self.relationships[character_a][character_b]["relationship_score"] += 1
        elif interaction_type == "negative":
            self.relationships[character_a][character_b]["relationship_score"] -= 1

        # Update last interaction timestamp
        self.relationships[character_a][character_b]["last_interaction"] = datetime.now().isoformat()

        # Save changes
        self.save_relationships()

    def get_relationship(self, character_a, character_b):
        """Get the relationship data between two characters."""
        if character_a in self.relationships and character_b in self.relationships[character_a]:
            return self.relationships[character_a][character_b]
        return None

    def prune_old_relationships(self):
        """Remove relationships that have not been interacted with in over a year."""
        one_year_ago = datetime.now().isoformat()
        for character_a in list(self.relationships.keys()):
            for character_b in list(self.relationships[character_a].keys()):
                last_interaction = self.relationships[character_a][character_b]["last_interaction"]
                if datetime.fromisoformat(last_interaction) < one_year_ago:
                    del self.relationships[character_a][character_b]
            if not self.relationships[character_a]:  # Remove character if no relationships left
                del self.relationships[character_a]
        self.save_relationships()

    def print_relationships(self):
        """Print all relationships for debugging purposes."""
        for character_a, relationships in self.relationships.items():
            for character_b, data in relationships.items():
                print(f"{character_a} -> {character_b}: {data['relationship_score']} (Last Interaction: {data['last_interaction']})")
