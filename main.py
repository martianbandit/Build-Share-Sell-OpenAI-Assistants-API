import openai
import streamlit as st
import time
import os
import zipfile
import yaml
 
from inference_assistant import inference
from utils import create_assistant_from_config_file, upload_to_openai, export_assistant

st.set_page_config(
    page_title="Chatbot Le Spéc'IA'liste du Vrac :van:",
    page_icon="💻",
    layout="centered",
    
    menu_items={
        'Obtenir de l\'aide': 'martianbandit@icloud.com',
        'Report a bug': "https://github.com/IntelligenzaArtificiale/Build-Share-Sell-OpenAI-Assistants-API/issues",
        'conditions d\'utilisations': "# This is a simple web app to build, share and sell OpenAI Assistants API\n\n"
    }
)
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Accueil","Inscription/connexion", "Chatbot", "conditions d'utilisations", "Obtenir de l\'aide"])
st.image("./asset/cti43y3h.png")
st.title("🤖 :gray[Le Spéc'IA'liste du Vrac]")

st.sidebar.image("./asset/openai-logomark.png", width=270)
st.sidebar.title(":gear: :red[Descriptions des Produits et Services]")

utiliter = st.selectbox("🤖 salut! Quels Assistants voulez vous utiliser?,", ("Charbonneau l'expert", "Le Spéc'IA'liste du Vrac"))

if utiliter != "Assistant Le Spéc'IA'liste du Vrac":
    scelta_creazione = st.selectbox(
        '💻 Voulez-vous créer un assistant de toutes pièces ou importer un assistant ?',
        ('Créer un Assistant depuis des Scratch', 'Importer un Assistant depuis .iaItaliaBotConfig'),
        index=0
    )

openaiKey = st.text_input("🔑 Inserrez votre cle api ici")
if openaiKey:
    os.environ["OPENAI_API_KEY"] = openaiKey
    openai.api_key = openaiKey
    client = openai.OpenAI()

    if utiliter == "Créer ou importer un assistant":
        if scelta_creazione == "Créer un Assistant depuis des Scratch":
            col1, col2 = st.columns(2)

            with col1:
                nome_assistente = st.text_input("👶 Inserrer le nom de l'assistant")

            with col2:
                modello_assistente = st.selectbox(
                    '🛒 Choissisez le modèle pour votre assistant',
                    ('gpt-4-1106-preview', 'gpt-4'),
                    index=0
                )

            if nome_assistente and modello_assistente:
                prompt_sistema = st.text_area("📄 Écrire les instructions de votre assistant")

                carica_file = st.checkbox("📚 Voulez vous joindre des documents comme base de connaissances?")

                stored_file = []
                if carica_file:
                    file_up = st.file_uploader("📚 télécharger vos documents", type=['.c', '.cpp', '.ipynb', '.docx', '.html', '.java', '.json', '.md', '.pdf', '.php', '.pptx', '.py', '.py', '.rb', '.tex', '.txt'], accept_multiple_files=True)
                    if file_up:
                        if len(file_up) > 20:
                            st.error("🛑 Le maximum de document es de 20")
                            st.stop()
                        st.info("HÉ, n'oubliez pas de cliquer sur le bouton « Télécharger le fichier » pour télécharger les fichiers sur OpenAI.")
                        if st.button("📩 Télécharger documents"):
                            with st.status("📡 Téléchargement vers le serveur OpenAI...", expanded=True) as status:
                                for file in file_up:
                                    time.sleep(2)
                                    status.update(label="🛰 Fichiers téléchargés: " + file.name)
                                    with open(file.name, "wb") as f:
                                        f.write(file.getbuffer())
                                    additional_file_id = upload_to_openai(file)
                                    if additional_file_id:
                                        st.write("Fichiers téléchargés avec succès: " + file.name + " with ID: " + additional_file_id)
                                        stored_file.append(additional_file_id)
                                st.write("👌 Fichiers téléchargés avec succès: " + str(len(stored_file)))
                                if 'id_file' not in st.session_state:
                                    st.session_state.id_file = []
                                st.session_state.id_file = stored_file
                                status.update(label="Fichiers téléchargés avec succès", state="completer", expanded=False)

                if st.button("🤖 Créer un Assistant") and prompt_sistema:
                    with st.status("⏲creation de l'Assistant en progression...", expanded=True) as status:
                        time.sleep(2)
                        status.update(label="🧐 Configuration de l'assistant...", state="En attente...")
                        time.sleep(2)
                        if "id_file" in st.session_state and len(st.session_state.id_file) > 0:
                            status.update(label="📡 Créer un assistant avec fichier et récupération...", state="running")
                            my_assistant = client.beta.assistants.create(
                                instructions=prompt_sistema,
                                name=nome_assistente,
                                tools=[{"type": "récupération"}],
                                model=modello_assistente,
                                file_ids=st.session_state.id_file,
                            )
                            st.write("👌 Assistant avec fichier et récupération créé avec succès!")
                        else:
                            
                            my_assistant = client.beta.assistants.create(
                                instructions=prompt_sistema,
                                name=nome_assistente,
                                model=modello_assistente,
                            )
                            status.update(label="👌 Assistant avec fichier et récupération créé avec succès!", state="complêté", expanded=False)


                        time.sleep(1)

                        st.success("✅ Assistant créé avec succès!")
                        st.info("🆗 ID de l'assistant: " + my_assistant.id)
                        st.error("⛔ Pensez à sauvegarder l'identifiant de l'assistant pour l'utiliser plus tard")
                        cola, colb = st.columns(2)
                        cola.info("📥 Pour utiliser l'assistant, copiez l'identifiant et collez-le dans la section 'Utiliser un assistant'")
                        colb.info("📤 Pour partager l'assistant, téléchargez le fichier de configuration de l'assistant et envoyez-le")


                    col3, col4 = st.columns(2)
                    #crea un bottone per scaricare un file.txt con l'ID dell'assistente
                    col3.download_button(
                        label="🗂 Download ID Assistant",
                        data="ASSISTANT ID : " + my_assistant.id + "\nOpenAI API Key: " + openaiKey,
                        file_name="id_ASSISTANT_" + nome_assistente.replace(" ", "_") + ".txt",
                        mime="text/plain",
                    )

                    with st.spinner("📥construction du Fichier de configuration de l'assistant  ..."):
                        data_to_export = export_assistant(nome_assistente, modello_assistente, prompt_sistema, file_up)
                        
                        col4.download_button(
                            label="🗂 Télécharger le fichier de configuration de l'assistant",
                            data=data_to_export,
                            file_name=nome_assistente + ".iaItaliaBotConfig",
                            mime="application/zip",
                        )

                    
                    st.balloons()


        else:
            file_up = st.file_uploader("📥 Upload .iaItaliaBotConfig", type=['.iaItaliaBotConfig'], accept_multiple_files=False)
            if file_up:
                if st.button("🤖 Imprter et Construire un Assistant"):
                    client = openai.OpenAI()
                    

                    with st.status("⏲ creation de l'Assistant en progression...", expanded=True) as status:
                        time.sleep(0.5)
                        status.update(label="Extraction et chargement de fichiers...", state="En cours...")
                        time.sleep(0.5)
                        my_assistant = create_assistant_from_config_file(file_up, client)
                        status.update(label="Assistant importé créé avec succès", state="complete")

                        st.success("✅ Assistant créé avec succès")
                        st.info("🆗 ID de votre assistant: " + my_assistant.id)
                        st.error("⛔ Pensez à sauvegarder l'identifiant de l'assistant pour l'utiliser plus tard")
                        cola, colb = st.columns(2)
                        cola.info("📥 Pour utiliser l'assistant, copiez l'identifiant et collez-le dans la section 'Utiliser un assistant'")
                        colb.info("📤 Pour partager l'assistant, téléchargez le fichier de configuration de l'assistant et envoyez-le")

                    st.download_button(
                        label="🗂 Télécharger ID Assistant",
                        data="ASSISTANT ID : " + my_assistant.id + "\nOpenAI API Key: " + openaiKey,
                        file_name="id_ASSISTANT.txt",
                        mime="text/plain",
                    )
        


    else:
        # Inferenza con Assistente

        id_assistente = st.text_input("🆔 Inserrez l'ID de  l'assistant")

        if id_assistente:
            try: 
                inference(id_assistente)
            except Exception as e:
                st.error("🛑 Il Semble avoir un problème avec les Server de OpenAI ")
                st.error(e)
                if st.button("🔄 Reprise..."):
                    st.rerun()

html_chat = "<center><h6>🤗 Visitez notre site web ou notre page facebook pour d'autres détails 🤗</h6>"
html_chat += '<br><a href="https://specialisteduvrac.com"></a><center><br>'
st.markdown(html_chat, unsafe_allow_html=True)
st.sidebar.write(":hammer::gear: :rainbow[Cet application est fièrement propulsé par:]www.Gpts-Index.com")
st.sidebar.image("./asset/cti43y3h.png", width=70),("./asset/openai-logomark.png", width=68)
st.sidebar.write(" :wrench: ")
