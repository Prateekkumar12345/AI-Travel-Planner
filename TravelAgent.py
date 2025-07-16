import requests
from bs4 import BeautifulSoup
from serpapi import GoogleSearch
import gradio as gr
import os
import groq
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np




class DestinationInfoRetriever:
    def __init__(self, serpapi_key):
        """
        Initialize the destination information retriever

        Args:
            serpapi_key (str): API key for SerpAPI
        """
        self.serpapi_key = serpapi_key
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = faiss.IndexFlatL2(384)
        self.knowledge_base = []

    def fetch_destination_info(self, destination):
        """
        Fetch comprehensive information about a destination

        Args:
            destination (str): Name of the destination

        Returns:
            dict: Destination information including descriptions, images, and details
        """
        try:

            overview = self._get_wikipedia_overview(destination)


            images = self._get_destination_images(destination)


            hotels = self._get_destination_hotels(destination)


            self._build_knowledge_base(destination)

            return {
                "overview": overview,
                "images": images,
                "hotels": hotels
            }
        except Exception as e:
            return {"error": str(e)}

    def _build_knowledge_base(self, destination):
        """
        Build a knowledge base for the destination using SerpAPI and Wikipedia

        Args:
            destination (str): Name of the destination
        """
        try:

            attractions = self._get_destination_attractions(destination)


            restaurants = self._get_destination_restaurants(destination)


            self.knowledge_base = attractions + restaurants


            embeddings = self.encoder.encode(self.knowledge_base)
            self.index.add(np.array(embeddings))
        except Exception as e:
            print(f"Error building knowledge base: {str(e)}")

    def _get_wikipedia_overview(self, destination):
        """
        Retrieve destination overview from Wikipedia

        Args:
            destination (str): Name of the destination

        Returns:
            str: Wikipedia overview of the destination
        """
        try:

            url = f"https://en.wikipedia.org/wiki/{destination.replace(' ', '_')}"


            response = requests.get(url)
            response.raise_for_status()


            soup = BeautifulSoup(response.text, 'html.parser')


            first_paragraph = soup.find('div', class_='mw-parser-output').find('p', class_=False)

            return first_paragraph.text if first_paragraph else "No overview available."
        except Exception:
            return "Unable to retrieve destination overview."

    def _get_destination_images(self, destination):
        """
        Retrieve destination images using SerpAPI

        Args:
            destination (str): Name of the destination

        Returns:
            list: URLs of destination images
        """
        try:

            params = {
                "engine": "google_images",
                "q": f"{destination} tourist attractions",
                "api_key": self.serpapi_key
            }


            search = GoogleSearch(params)
            results = search.get_dict()


            images = [
                img.get('original')
                for img in results.get('images_results', [])[:6]
                if img.get('original')
            ]

            return images
        except Exception:
            return []

    def _get_destination_hotels(self, destination):
        """
        Retrieve hotel information using SerpAPI

        Args:
            destination (str): Name of the destination

        Returns:
            list: Information about top hotels
        """
        try:

            params = {
                "engine": "google_travel",
                "q": f"top hotels in {destination}",
                "api_key": self.serpapi_key
            }


            search = GoogleSearch(params)
            results = search.get_dict()

            hotels = []
            for hotel in results.get('hotels_results', []):
                hotels.append({
                    "name": hotel.get('name', 'Unknown'),
                    "rating": hotel.get('rating', 'N/A'),
                    "price": hotel.get('price', 'N/A'),
                    "description": hotel.get('description', 'No description available')
                })

            return hotels[:5]
        except Exception:
            return []

    def _get_destination_attractions(self, destination):
        """
        Retrieve top attractions for a destination using SerpAPI

        Args:
            destination (str): Name of the destination

        Returns:
            list: Descriptions of top attractions
        """
        try:

            params = {
                "engine": "google",
                "q": f"top attractions in {destination}",
                "api_key": self.serpapi_key
            }


            search = GoogleSearch(params)
            results = search.get_dict()


            attractions = [
                result.get('snippet', '')
                for result in results.get('organic_results', [])[:5]
            ]

            return attractions
        except Exception:
            return []

    def _get_destination_restaurants(self, destination):
        """
        Retrieve top restaurants for a destination using SerpAPI

        Args:
            destination (str): Name of the destination

        Returns:
            list: Descriptions of top restaurants
        """
        try:

            params = {
                "engine": "google",
                "q": f"top restaurants in {destination}",
                "api_key": self.serpapi_key
            }


            search = GoogleSearch(params)
            results = search.get_dict()


            restaurants = [
                result.get('snippet', '')
                for result in results.get('organic_results', [])[:5]
            ]

            return restaurants
        except Exception:
            return []

    def retrieve_relevant_info(self, query):
        """
        Retrieve relevant information from the knowledge base using FAISS

        Args:
            query (str): User's query

        Returns:
            str: Relevant information from the knowledge base
        """
        try:

            query_embedding = self.encoder.encode([query])


            _, indices = self.index.search(np.array(query_embedding), k=3)


            relevant_info = [self.knowledge_base[i] for i in indices[0]]
            return "\n".join(relevant_info)
        except Exception as e:
            return f"Error retrieving information: {str(e)}"





class TravelPlannerAssistant:
    def __init__(self, serpapi_key, groq_api_key):
        """
        Initialize the Travel Planner Assistant

        Args:
            serpapi_key (str): API key for SerpAPI
            groq_api_key (str): API key for Groq
        """
        self.serpapi_key = serpapi_key
        self.client = groq.Client(api_key=groq_api_key)
        self.destination_retriever = DestinationInfoRetriever(serpapi_key)

    def generate_travel_itinerary(self, user_preferences):
        """
        Generate a personalized travel itinerary using Groq's prompt-based interaction

        Args:
            user_preferences (dict): User's travel preferences

        Returns:
            str: Detailed travel itinerary
        """

        system_prompt = """You are an expert travel planner. Your goal is to create a highly personalized and detailed travel itinerary based on the user's specific preferences.

        Consider the following guidelines:
        1. Tailor recommendations to the user's interests, budget, and travel style
        2. Include a mix of popular attractions and off-the-beaten-path experiences
        3. Provide practical details like estimated travel times, costs, and logistics
        4. Suggest restaurants, activities, and accommodations that match the traveler's profile
        5. Include cultural insights and local recommendations
        6. Ensure the itinerary is realistic and well-paced
        """


        user_prompt = f"""Please create a detailed travel itinerary for my trip to {user_preferences['destination']}:

        Trip Details:
        - Destination: {user_preferences['destination']}
        - Duration: {user_preferences['duration']} days
        - Travel Style: {user_preferences['travel_style']}
        - Interests: {', '.join(user_preferences['interests'])}
        - Budget: {user_preferences['budget']}
        - Travelers: {user_preferences['travelers']}
        - Season/Month: {user_preferences['travel_month']}

        Additional Context:
        - Specific activities I'm interested in: {user_preferences.get('specific_activities', 'None specified')}
        - Dietary restrictions: {user_preferences.get('dietary_restrictions', 'None')}
        - Mobility considerations: {user_preferences.get('mobility_considerations', 'None')}

        Could you create a day-by-day itinerary that captures these preferences? Include recommended attractions, dining options, transportation details, and any special recommendations."""


        try:
            response = self.client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=4000
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating itinerary: {str(e)}"

    def handle_user_query(self, query, destination):
        """
        Handle user queries related to a destination using RAG

        Args:
            query (str): User's query (e.g., "good food in Paris")
            destination (str): Destination name

        Returns:
            tuple: Response text and generated image URLs
        """
        try:

            relevant_info = self.destination_retriever.retrieve_relevant_info(query)


            system_prompt = """You are a helpful travel assistant. Provide detailed and accurate answers to user queries about destinations, including recommendations for food, hotels, and activities based on their budget."""

            user_prompt = f"""User Query: {query}
            Destination: {destination}

            Relevant Information:
            {relevant_info}

            Provide a detailed response with recommendations. Include:
            1. Specific places or activities
            2. Estimated costs
            3. Any additional tips or insights"""


            response = self.client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=2000
            )


            images = self.destination_retriever._get_destination_images(f"{destination} {query}")

            return response.choices[0].message.content, images
        except Exception as e:
            return f"Error handling query: {str(e)}", []

    def main_interface(self):
        """
        Create Gradio interface for travel planning
        """
        with gr.Blocks() as demo:
            gr.Markdown("# 🌍 AI Travel Planner")


            destination = gr.Textbox(label="Where would you like to travel?")


            duration = gr.Slider(minimum=1, maximum=30, step=1, label="Trip Duration (days)")


            travel_style = gr.Dropdown(
                choices=[
                    "Leisure",
                    "Adventure",
                    "Cultural Exploration",
                    "Luxury",
                    "Budget",
                    "Family-Friendly",
                    "Solo Traveler"
                ],
                label="Travel Style"
            )


            interests = gr.CheckboxGroup(
                choices=[
                    "History", "Food", "Nature", "Art", "Architecture",
                    "Museums", "Beaches", "Hiking", "Shopping", "Nightlife"
                ],
                label="Select Your Interests"
            )


            budget = gr.Dropdown(
                choices=[
                    "Budget (<$1000)",
                    "Moderate (
3000)",
                    "Luxury (
10000)",
                    "Premium (>$10000)"
                ],
                label="Budget Range"
            )


            travelers = gr.Dropdown(
                choices=[
                    "Solo", "Couple", "Family", "Friends Group", "Business"
                ],
                label="Travel Group Type"
            )


            travel_month = gr.Dropdown(
                choices=[
                    "January", "February", "March", "April", "May",
                    "June", "July", "August", "September", "October",
                    "November", "December"
                ],
                label="Preferred Travel Month"
            )


            query_input = gr.Textbox(label="Ask a question (e.g., 'good food in Paris')")


            generate_itinerary_btn = gr.Button("Generate My Personalized Itinerary")
            generate_query_response_btn = gr.Button("Get Answer")


            itinerary_output = gr.Textbox(label="Your Personalized Travel Itinerary")
            query_output = gr.Textbox(label="Query Response")
            destination_images = gr.Gallery(label="Destination Highlights")


            generate_itinerary_btn.click(
                fn=self.generate_personalized_trip,
                inputs=[destination, duration, travel_style, interests, budget, travelers, travel_month],
                outputs=[itinerary_output, destination_images]
            )

            generate_query_response_btn.click(
                fn=self.handle_user_query,
                inputs=[query_input, destination],
                outputs=[query_output, destination_images]
            )

        return demo

    def generate_personalized_trip(self, destination, duration, travel_style,
                                    interests, budget, travelers, travel_month):
        """
        Generate a complete personalized travel experience

        Returns:
            tuple: Itinerary text and destination images
        """

        user_preferences = {
            'destination': destination,
            'duration': duration,
            'travel_style': travel_style,
            'interests': interests,
            'budget': budget,
            'travelers': travelers,
            'travel_month': travel_month
        }


        itinerary = self.generate_travel_itinerary(user_preferences)


        destination_info = self.destination_retriever.fetch_destination_info(destination)
        images = destination_info.get('images', [])

        return itinerary, images



def main():

    SERPAPI_KEY = os.getenv('SERPAPI_KEY', '')
    GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')


    travel_planner = TravelPlannerAssistant(SERPAPI_KEY, GROQ_API_KEY)


    demo = travel_planner.main_interface()
    demo.launch(debug=True)

if __name__ == "__main__":
    main()
     
