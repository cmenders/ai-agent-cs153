"""
Functionality for managing reading lists/collections of papers.
"""
import json
import os

class ReadingLists:
    def __init__(self, lists_file="reading_lists.json"):
        self.lists_file = lists_file
        self.reading_lists = self._load_lists()
    
    def _load_lists(self):
        """Load reading lists from file if it exists, otherwise return empty dict"""
        if os.path.exists(self.lists_file):
            try:
                with open(self.lists_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading reading lists: {e}")
                return {}
        return {}
    
    def _save_lists(self):
        """Save reading lists to file"""
        try:
            with open(self.lists_file, 'w') as f:
                json.dump(self.reading_lists, f, indent=2)
        except Exception as e:
            print(f"Error saving reading lists: {e}")
    
    def create_list(self, conversation_id, list_name):
        """
        Create a new reading list
        
        Parameters:
        conversation_id (str): ID of the conversation (e.g., channel ID)
        list_name (str): Name of the reading list
        
        Returns:
        bool: True if successful, False otherwise
        """
        # Initialize conversation dict if it doesn't exist
        if conversation_id not in self.reading_lists:
            self.reading_lists[conversation_id] = {}
        
        # Check if list already exists
        if list_name in self.reading_lists[conversation_id]:
            return False
        
        # Create the list
        self.reading_lists[conversation_id][list_name] = []
        
        self._save_lists()
        return True
    
    def add_paper_to_list(self, conversation_id, list_name, paper_key):
        """
        Add a paper to a reading list
        
        Parameters:
        conversation_id (str): ID of the conversation
        list_name (str): Name of the reading list
        paper_key (str): Key identifying the paper
        
        Returns:
        bool: True if successful, False otherwise
        """
        try:
            # Check if conversation and list exist
            if (conversation_id not in self.reading_lists or 
                list_name not in self.reading_lists[conversation_id]):
                return False
            
            # Check if paper is already in the list
            if paper_key in self.reading_lists[conversation_id][list_name]:
                return True  # Already in list, still consider successful
            
            # Add the paper to the list
            self.reading_lists[conversation_id][list_name].append(paper_key)
            
            self._save_lists()
            return True
        except Exception:
            return False
    
    def remove_paper_from_list(self, conversation_id, list_name, paper_key):
        """
        Remove a paper from a reading list
        
        Parameters:
        conversation_id (str): ID of the conversation
        list_name (str): Name of the reading list
        paper_key (str): Key identifying the paper
        
        Returns:
        bool: True if successful, False otherwise
        """
        try:
            # Check if conversation and list exist
            if (conversation_id not in self.reading_lists or 
                list_name not in self.reading_lists[conversation_id]):
                return False
            
            # Check if paper is in the list
            if paper_key not in self.reading_lists[conversation_id][list_name]:
                return False
            
            # Remove the paper from the list
            self.reading_lists[conversation_id][list_name].remove(paper_key)
            
            self._save_lists()
            return True
        except Exception:
            return False
    
    def delete_list(self, conversation_id, list_name):
        """
        Delete a reading list
        
        Parameters:
        conversation_id (str): ID of the conversation
        list_name (str): Name of the reading list
        
        Returns:
        bool: True if successful, False otherwise
        """
        try:
            # Check if conversation and list exist
            if (conversation_id not in self.reading_lists or 
                list_name not in self.reading_lists[conversation_id]):
                return False
            
            # Delete the list
            del self.reading_lists[conversation_id][list_name]
            
            self._save_lists()
            return True
        except Exception:
            return False
    
    def get_lists(self, conversation_id):
        """
        Get all reading lists for a conversation
        
        Parameters:
        conversation_id (str): ID of the conversation
        
        Returns:
        dict: Reading lists for the conversation
        """
        if conversation_id not in self.reading_lists:
            return {}
        
        return self.reading_lists[conversation_id]
    
    def get_list(self, conversation_id, list_name):
        """
        Get a specific reading list
        
        Parameters:
        conversation_id (str): ID of the conversation
        list_name (str): Name of the reading list
        
        Returns:
        list: List of paper keys in the reading list, or None if not found
        """
        if conversation_id not in self.reading_lists:
            return None
        
        return self.reading_lists[conversation_id].get(list_name, None)
    
    def format_lists(self, conversation_id, list_name=None, paper_info=None):
        """
        Format reading lists for display
        
        Parameters:
        conversation_id (str): ID of the conversation
        list_name (str, optional): Name of a specific list to format. If None, format all lists
        paper_info (dict, optional): Dictionary mapping paper_keys to paper info
        
        Returns:
        str: Formatted reading lists
        """
        # If a specific list was requested
        if list_name:
            paper_keys = self.get_list(conversation_id, list_name)
            
            if paper_keys is None:
                return f"Reading list '{list_name}' not found."
            
            if not paper_keys:
                return f"Reading list '{list_name}' is empty."
            
            result = f"Reading List: {list_name}\n\n"
            
            # Format the papers in the list
            for i, paper_key in enumerate(paper_keys, 1):
                paper_title = "Unknown Paper"
                if paper_info and paper_key in paper_info:
                    paper_title = f"{paper_info[paper_key]['title']} ({paper_info[paper_key]['year']})"
                
                result += f"{i}. {paper_title}\n"
            
            return result
        
        # Format all lists
        lists = self.get_lists(conversation_id)
        
        if not lists:
            return "No reading lists found."
        
        result = "Reading Lists:\n\n"
        
        for list_name, paper_keys in lists.items():
            result += f"📚 {list_name} ({len(paper_keys)} papers)\n"
        
        result += "\nUse '!reading_list view <list_name>' to see papers in a specific list."
        
        return result
