"""
Functionality for managing research notes associated with papers.
"""
import json
import os
from datetime import datetime

class ResearchNotes:
    def __init__(self, notes_file="research_notes.json"):
        self.notes_file = notes_file
        self.notes = self._load_notes()
    
    def _load_notes(self):
        """Load notes from file if it exists, otherwise return empty dict"""
        if os.path.exists(self.notes_file):
            try:
                with open(self.notes_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading notes: {e}")
                return {}
        return {}
    
    def _save_notes(self):
        """Save notes to file"""
        try:
            with open(self.notes_file, 'w') as f:
                json.dump(self.notes, f, indent=2)
        except Exception as e:
            print(f"Error saving notes: {e}")
    
    def add_note(self, conversation_id, paper_key, note_text):
        """
        Add a note to a paper
        
        Parameters:
        conversation_id (str): ID of the conversation (e.g., channel ID)
        paper_key (str): Key identifying the paper
        note_text (str): The note to add
        
        Returns:
        bool: True if successful, False otherwise
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Initialize conversation dict if it doesn't exist
        if conversation_id not in self.notes:
            self.notes[conversation_id] = {}
        
        # Initialize paper list if it doesn't exist
        if paper_key not in self.notes[conversation_id]:
            self.notes[conversation_id][paper_key] = []
        
        # Add the note
        self.notes[conversation_id][paper_key].append({
            "timestamp": timestamp,
            "text": note_text
        })
        
        self._save_notes()
        return True
    
    def get_notes(self, conversation_id, paper_key=None):
        """
        Get notes for a paper or all papers in a conversation
        
        Parameters:
        conversation_id (str): ID of the conversation
        paper_key (str, optional): Key identifying the paper. If None, return all notes
        
        Returns:
        dict: Notes for the paper(s)
        """
        if conversation_id not in self.notes:
            return {}
        
        if paper_key:
            return {paper_key: self.notes[conversation_id].get(paper_key, [])}
        
        return self.notes[conversation_id]
    
    def delete_note(self, conversation_id, paper_key, note_index):
        """
        Delete a specific note
        
        Parameters:
        conversation_id (str): ID of the conversation
        paper_key (str): Key identifying the paper
        note_index (int): Index of the note to delete (0-based)
        
        Returns:
        bool: True if successful, False otherwise
        """
        try:
            if (conversation_id in self.notes and 
                paper_key in self.notes[conversation_id] and 
                0 <= note_index < len(self.notes[conversation_id][paper_key])):
                
                self.notes[conversation_id][paper_key].pop(note_index)
                self._save_notes()
                return True
            return False
        except Exception:
            return False
    
    def format_notes(self, conversation_id, paper_key=None, paper_info=None):
        """
        Format notes for display
        
        Parameters:
        conversation_id (str): ID of the conversation
        paper_key (str, optional): Key identifying the paper. If None, format all notes
        paper_info (dict, optional): Dictionary mapping paper_keys to paper info
        
        Returns:
        str: Formatted notes
        """
        notes_dict = self.get_notes(conversation_id, paper_key)
        
        if not notes_dict:
            return "No notes found."
        
        result = "Research Notes:\n\n"
        
        for pk, notes in notes_dict.items():
            # Get paper title if paper_info is provided
            paper_title = "Unknown Paper"
            if paper_info and pk in paper_info:
                paper_title = f"{paper_info[pk]['title']} ({paper_info[pk]['year']})"
            
            result += f"Paper: {paper_title}\n"
            
            if not notes:
                result += "  No notes for this paper.\n\n"
                continue
            
            for i, note in enumerate(notes):
                result += f"  Note {i+1} [{note['timestamp']}]:\n"
                result += f"  {note['text']}\n\n"
        
        return result
    
    def clear_notes(self, conversation_id, paper_key=None):
        """
        Clear all notes for a paper or conversation
        
        Parameters:
        conversation_id (str): ID of the conversation
        paper_key (str, optional): Key identifying the paper. If None, clear all notes
        
        Returns:
        bool: True if successful, False otherwise
        """
        try:
            if conversation_id not in self.notes:
                return False
            
            if paper_key:
                if paper_key in self.notes[conversation_id]:
                    self.notes[conversation_id][paper_key] = []
                    self._save_notes()
                    return True
                return False
            
            # Clear all notes for the conversation
            self.notes[conversation_id] = {}
            self._save_notes()
            return True
        except Exception:
            return False