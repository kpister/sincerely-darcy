import os
import io
import urllib.parse
import requests
from google.cloud import vision
import cohere
from dotenv import load_dotenv


# website: https://sincereley-darcy.unicornplatform.page/

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "keys.json"
config = load_dotenv()

# use google document AI to extract text from png
def extract_text_from_png(file_path):
    client = vision.ImageAnnotatorClient()
    with io.open(file_path, "rb") as image_file:
        content = image_file.read()
    image = vision.Image(content=content)
    response = client.document_text_detection(image=image)
    document = response.full_text_annotation
    return document.text


# generate response with cohere
def generate_response(text):
    preprompt = ""
    co = cohere.Client(config["cohere_api_key"])
    response = co.generate(
        model="xlarge",
        prompt=preprompt + text,
        max_tokens=300,
        temperature=0.8,
        k=0,
        p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop_sequences=["Darcy."],
        return_likelihoods="NONE",
    )

    return response.generations[0].text


def send_card(message, address):
    base_url = "https://api.handwrytten.com/v1"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    # send card to address
    order_url = base_url + "/orders/singleStepOrder"
    login = "kaiser@pister.dev"
    login = urllib.parse.quote(login)
    message = urllib.parse.quote(message)
    card_id = "70889"
    font_label = "Proper Jeff"
    credit_card_id = "39830"

    sender_name = "Pister Kaiser"
    sender_address1 = "20 Camino Del Diablo"
    sender_address2 = ""
    sender_city = "Orinda"
    sender_state = "CA"
    sender_zip = "94563"

    recipient_name = urllib.parse.quote(address["name"])
    recipient_address1 = urllib.parse.quote(address["address1"])
    recipient_address2 = urllib.parse.quote(address["address2"])
    recipient_city = urllib.parse.quote(address["city"])
    recipient_state = urllib.parse.quote(address["state"])
    recipient_zip = urllib.parse.quote(address["zip"])
    password = config["password"]

    data = f"login={login}&password={password}&message={message}&card_id={card_id}&font_label={font_label}&credit_card_id={credit_card_id}&sender_name={sender_name}&sender_address1={sender_address1}&sender_address2={sender_address2}&sender_city={sender_city}&sender_state={sender_state}&sender_zip={sender_zip}&recipient_name={recipient_name}&recipient_address1={recipient_address1}&recipient_address2={recipient_address2}&recipient_city={recipient_city}&recipient_state={recipient_state}&recipient_zip={recipient_zip}"

    return requests.post(order_url, data=data, headers=headers)


def load_address():
    address = {
        "name": "Kaiser Pister",
        "address1": "640 W. Wilson St.",
        "address2": "Unit 333",
        "city": "Madison",
        "state": "WI",
        "zip": "53703",
    }
    return address


def main():
    file_name = os.path.abspath("img.jpg")
    note = extract_text_from_png(file_name)
    message = generate_response(note)
    address = load_address()
    handwrytten_response = send_card(message, address)
    if handwrytten_response.status_code == 200:
        print("success")
    else:
        print("failure")
