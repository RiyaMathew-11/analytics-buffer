    def default_api_call(events: List[Dict[str, Any]]):
        """
        Mock API call that simulates network delay.
        
        In real implementation, this would be replaced with actual HTTP request:
        
        async def real_api_call(events):
            async with aiohttp.ClientSession() as session:
                async with session.post(API_URL, json=events) as response:
                    response.raise_for_status()
        
        Args:
            events: List of events to send
        
        Raises:
            Exception: Simulated API failure (for testing)
        """
        # Simulate network delay
        time.sleep(0.1)
        
        # Mock successful API response
        logger.debug(f"Mock API received {len(events)} events")
        
        # In production, make the actual HTTP request here:
        # response = requests.post('https://api.example.com/events', json=events)
        # response.raise_for_status()