
import streamlit as st
import pandas as pd
import random
import time
from fpdf import FPDF
import tempfile

st.set_page_config(page_title="Catering Companion", layout="centered", page_icon="🍴")

# Load style

# App setup
affirmations = [
    "You're doing great work, keep pushing.",
    "Today's prep is tomorrow's peace.",
    "Every tray you prep is a step closer to success.",
]

# Track checked ingredients
if "checked_ingredients" not in st.session_state:
    st.session_state.checked_ingredients = set()

def generate_shopping_list_pdf(sections):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for category, lines in sections.items():
        title = category[0] if isinstance(category, tuple) else category
        pdf.set_font("Arial", "B", 14)
        pdf.cell(200, 10, txt=title.upper(), ln=True)
        pdf.set_font("Arial", size=12)
        for line in lines:
            pdf.cell(200, 10, txt=line, ln=True)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(temp_file.name)
    return temp_file

# Load and scale recipe CSV
df = pd.read_csv("master_recipe_template.csv")
unique_recipes = df["RecipeName"].unique()

recipe_name = st.selectbox("Choose a recipe:", unique_recipes)
num_guests = st.number_input("Number of guests:", min_value=1, value=10, step=1)

recipe_df = df[df["RecipeName"] == recipe_name].copy()
base_servings = recipe_df["BaseServings"].iloc[0]
scaling_factor = num_guests / base_servings

recipe_df["ScaledQuantity"] = recipe_df["Quantity"] * scaling_factor

# Show shopping list preview with checkboxes
st.subheader("Shopping List Preview")
for idx, row in recipe_df.iterrows():
    label = f"{row['ScaledQuantity']} {row['Unit']} {row['Ingredient']}"
    if st.checkbox(label, key=f"check_{idx}"):
        st.session_state.checked_ingredients.add(row['Ingredient'])
    else:
        st.session_state.checked_ingredients.discard(row['Ingredient'])

# Filter out checked items for final list
filtered_df = recipe_df[~recipe_df["Ingredient"].isin(st.session_state.checked_ingredients)]

# Group by category for final list
grouped = filtered_df.groupby("Category")
final_sections = {}
for category, group in grouped:
    lines = [f"{row['ScaledQuantity']} {row['Unit']} {row['Ingredient']}" for _, row in group.iterrows()]
    final_sections[category] = lines

# Show final shopping list
st.markdown("---")
st.subheader("Final Shopping List")
for category, items in final_sections.items():
    st.markdown(f"**{category}**")
    for item in items:
        st.write(f"- {item}")

# PDF Export
if st.button("Export Shopping List to PDF"):
    pdf_file = generate_shopping_list_pdf(final_sections)
    with open(pdf_file.name, "rb") as file:
        st.download_button(
            label="Download PDF",
            data=file,
            file_name="shopping_list.pdf",
            mime="application/pdf"
        )

# Show recipe guide
st.markdown("---")
st.subheader("Recipe Guide")
steps = recipe_df.dropna(subset=["Method"])
if not steps.empty:
    for _, row in steps.iterrows():
        st.markdown(f"**{row['Ingredient']}**: {row['Method']}")
else:
    st.info("No recipe instructions provided for this dish.")
