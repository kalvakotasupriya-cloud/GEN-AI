import streamlit as st
import faiss
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import torch
import torchvision.transforms as transforms
import torchvision.models as models
from PIL import Image

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="KrishiSahay", layout="centered")
st.title("🌾 KrishiSahay - Offline Agriculture Assistant")

# ===============================
# 🌱 CHATBOT SECTION
# ===============================

st.markdown("### 🌱 Ask your agriculture questions")

language = st.selectbox("Select Answer Language", ["English", "Telugu"])

# -------- Load NLP Model --------
@st.cache_resource
def load_embed_model():
    return SentenceTransformer(
        "all-MiniLM-L6-v2",
        local_files_only=True
    )

# -------- Load FAISS --------
@st.cache_resource
def load_index():
    return faiss.read_index("kcc_index.faiss")

# -------- Load Data --------
@st.cache_data
def load_data():
    return pd.read_csv("clean_kcc.csv")

model = load_embed_model()
index = load_index()
df = load_data()

# -------- User Input --------
query = st.text_input("Type your question in English:")

if st.button("🔍 Get Answer"):

    if query.strip() == "":
        st.warning("Please enter a question.")
    else:
        query_embedding = model.encode([query])
        D, I = index.search(np.array(query_embedding), k=1)

        result = df.iloc[I[0][0]]
        full_answer = str(result["answer"])

        lines = full_answer.split("\n")
        english_part = lines[0]
        telugu_part = "\n".join(lines[1:]) if len(lines) > 1 else ""

        st.markdown("---")

        if language == "English":
            st.subheader("🌿 Answer")
            st.write(english_part)
        else:
            if telugu_part.strip():
                st.subheader("🌍 సమాధానం")
                st.write(telugu_part)
            else:
                st.warning("Telugu translation not available. Showing English.")
                st.write(english_part)

# ===============================
# 🐛 PEST DETECTION SECTION
# ===============================

st.markdown("---")
st.title("🐛 Pest / Disease Detection")

uploaded_file = st.file_uploader(
    "Upload leaf image",
    type=["jpg", "png", "jpeg"]
)

if uploaded_file is not None:

    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Uploaded Image", use_column_width=True)

    @st.cache_resource
    def load_pest_model():
        class_names = torch.load("class_names.pth")

        model = models.mobilenet_v2(weights=None)
        model.classifier[1] = torch.nn.Linear(
            model.last_channel,
            len(class_names)
        )

        model.load_state_dict(
            torch.load("pest_model.pth", map_location="cpu")
        )

        model.eval()
        return model, class_names

    model_pest, class_names = load_pest_model()

    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
    ])

    img_tensor = transform(image).unsqueeze(0)

    with torch.no_grad():
        outputs = model_pest(img_tensor)
        _, predicted = torch.max(outputs, 1)

    predicted_label = class_names[predicted.item()]

    st.subheader("🔎 Prediction Result")
    st.success(predicted_label)

    # Optional treatment suggestion
    treatment_dict = {
    "Apple___healthy":
        "The plant is healthy. Maintain proper irrigation and regular monitoring.",

    "Apple___Apple_scab":
        "Remove infected leaves and apply recommended fungicide such as captan or myclobutanil.",

    "Apple___Black_rot":
        "Prune infected branches and apply appropriate fungicide spray. Remove fallen fruits.",

    "Apple___Cedar_apple_rust":
        "Apply fungicide during early spring and remove nearby cedar trees if possible."
}

    st.markdown("### 🌿 Recommended Action")
    st.info(
        treatment_dict.get(
            predicted_label,
            "Consult agriculture officer for proper treatment."
        )
    )