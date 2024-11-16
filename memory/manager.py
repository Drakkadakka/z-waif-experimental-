class MemoryManager:
    def __init__(self):
        self.memories = {}
        
    def add_memory(self, author, context, platform):
        if author not in self.memories:
            self.memories[author] = []
        self.memories[author].append({
            "context": context,
            "platform": platform
        }) 