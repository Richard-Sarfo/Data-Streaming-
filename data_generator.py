"""
Real-Time E-Commerce Event Data Generator
Generates fake user events (views, purchases) and saves them as CSV files
"""

import os
import csv
import time
import random
from datetime import datetime, timedelta
from faker import Faker
import argparse
from pathlib import Path


class ECommerceEventGenerator:
    """Generate realistic e-commerce events"""
    
    def __init__(self, output_dir="./data/events", batch_size=100, delay_seconds=5):
        """
        Initialize the event generator
        
        Args:
            output_dir: Directory to save CSV files
            batch_size: Number of events per CSV file
            delay_seconds: Delay between batches in seconds
        """
        self.output_dir = output_dir
        self.batch_size = batch_size
        self.delay_seconds = delay_seconds
        self.fake = Faker()
        
        # Create output directory if it doesn't exist
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        
        # Sample data
        self.event_types = ["view", "add_to_cart", "remove_from_cart", "purchase", "wishlist"]
        self.product_categories = ["Electronics", "Clothing", "Home", "Books", "Sports"]
        self.users = [self.fake.user_name() for _ in range(50)]
        self.products = {
            "Electronics": [f"Laptop_{i}" for i in range(10)] + [f"Phone_{i}" for i in range(10)],
            "Clothing": [f"Shirt_{i}" for i in range(15)] + [f"Pants_{i}" for i in range(15)],
            "Home": [f"Sofa_{i}" for i in range(8)] + [f"Lamp_{i}" for i in range(8)],
            "Books": [f"Novel_{i}" for i in range(20)],
            "Sports": [f"Shoe_{i}" for i in range(12)] + [f"Racket_{i}" for i in range(8)]
        }
    
    def generate_event(self, event_timestamp):
        """
        Generate a single event
        
        Args:
            event_timestamp: Timestamp for the event
            
        Returns:
            Dictionary representing an event
        """
        category = random.choice(self.product_categories)
        product_id = random.choice(self.products[category])
        
        event = {
            "user_id": random.choice(self.users),
            "event_type": random.choice(self.event_types),
            "product_id": product_id,
            "product_category": category,
            "product_price": round(random.uniform(10, 1000), 2),
            "quantity": random.randint(1, 5),
            "timestamp": event_timestamp.isoformat(),
            "session_id": self.fake.uuid4(),
            "device": random.choice(["mobile", "desktop", "tablet"]),
            "country": self.fake.country_code(),
            "total_amount": round(random.uniform(10, 500), 2)
        }
        return event
    
    def save_batch_to_csv(self, events, batch_number):
        """
        Save a batch of events to a CSV file
        
        Args:
            events: List of event dictionaries
            batch_number: Batch number for filename
        """
        if not events:
            return
        
        filename = os.path.join(self.output_dir, f"events_batch_{batch_number:05d}.csv")
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = events[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(events)
        
        print(f"✓ Saved {len(events)} events to {filename}")
    
    def generate_continuous_stream(self, num_batches=None, verbose=True):
        """
        Generate events continuously (or for a fixed number of batches)
        
        Args:
            num_batches: Number of batches to generate (None = infinite)
            verbose: Print progress messages
        """
        batch_number = 0
        
        try:
            while num_batches is None or batch_number < num_batches:
                events = []
                base_timestamp = datetime.now()
                
                for i in range(self.batch_size):
                    # Add slight time offset to each event within batch
                    event_timestamp = base_timestamp + timedelta(milliseconds=i * 10)
                    event = self.generate_event(event_timestamp)
                    events.append(event)
                
                self.save_batch_to_csv(events, batch_number)
                batch_number += 1
                
                if verbose:
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
                          f"Batch {batch_number} generated. Waiting {self.delay_seconds}s...")
                
                time.sleep(self.delay_seconds)
        
        except KeyboardInterrupt:
            print(f"\n✓ Generator stopped. Total batches generated: {batch_number}")
    
    def generate_single_batch(self, batch_number=0):
        """
        Generate a single batch of events (useful for testing)
        
        Args:
            batch_number: Batch number for filename
        """
        events = []
        base_timestamp = datetime.now()
        
        for i in range(self.batch_size):
            event_timestamp = base_timestamp + timedelta(milliseconds=i * 10)
            event = self.generate_event(event_timestamp)
            events.append(event)
        
        self.save_batch_to_csv(events, batch_number)


def main():
    parser = argparse.ArgumentParser(
        description="Generate fake e-commerce events for streaming pipeline"
    )
    parser.add_argument(
        "--output-dir",
        default="./data/events",
        help="Output directory for CSV files (default: ./data/events)"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Number of events per batch (default: 100)"
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=5,
        help="Delay between batches in seconds (default: 5)"
    )
    parser.add_argument(
        "--num-batches",
        type=int,
        default=None,
        help="Number of batches to generate (default: infinite stream)"
    )
    parser.add_argument(
        "--single",
        action="store_true",
        help="Generate a single batch and exit"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("E-Commerce Event Data Generator")
    print("=" * 60)
    
    generator = ECommerceEventGenerator(
        output_dir=args.output_dir,
        batch_size=args.batch_size,
        delay_seconds=args.delay
    )
    
    if args.single:
        print(f"Generating single batch to {args.output_dir}")
        generator.generate_single_batch()
    else:
        print(f"Starting continuous stream generation...")
        print(f"Output directory: {args.output_dir}")
        print(f"Batch size: {args.batch_size} events")
        print(f"Batch interval: {args.delay}s")
        if args.num_batches:
            print(f"Number of batches: {args.num_batches}")
        print("-" * 60)
        generator.generate_continuous_stream(num_batches=args.num_batches)


if __name__ == "__main__":
    main()
