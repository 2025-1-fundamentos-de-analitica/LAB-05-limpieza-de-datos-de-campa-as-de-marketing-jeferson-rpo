"""
Escriba el codigo que ejecute la accion solicitada.
"""

# pylint: disable=import-outside-toplevel


import os
import zipfile
import pandas as pd
from datetime import datetime

def clean_campaign_data():
    """
    Limpia los datos de campañas de marketing desde archivos CSV comprimidos.
    Genera tres archivos: client.csv, campaign.csv y economics.csv en files/output/.
    """
    input_path = "files/input"
    output_path = "files/output"

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    df_total = pd.DataFrame()

    # Leer todos los .zip en files/input
    for archivo in os.listdir(input_path):
        if archivo.endswith(".zip"):
            zip_path = os.path.join(input_path, archivo)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                for csv_file in zip_ref.namelist():
                    with zip_ref.open(csv_file) as f:
                        df_temp = pd.read_csv(f)
                        df_total = pd.concat([df_total, df_temp], ignore_index=True)

    # Asegurar que los nombres de columnas no tengan espacios o símbolos extraños
    df_total.columns = [col.strip().lower().replace(" ", "_") for col in df_total.columns]

    # Asignar client_id si no existe
    if "client_id" not in df_total.columns:
        df_total.insert(0, "client_id", range(len(df_total)))

    # ----------- client.csv -----------
    df_client = df_total[[
        "client_id", "age", "job", "marital", "education",
        "credit_default", "mortgage"
    ]].copy()

    df_client["job"] = df_client["job"].str.replace(".", "", regex=False).str.replace("-", "_", regex=False)
    df_client["education"] = df_client["education"].str.replace(".", "_", regex=False)
    df_client["education"] = df_client["education"].replace("unknown", pd.NA)
    df_client["credit_default"] = df_client["credit_default"].apply(lambda x: 1 if str(x).lower() == "yes" else 0)
    df_client["mortgage"] = df_client["mortgage"].apply(lambda x: 1 if str(x).lower() == "yes" else 0)

    df_client.to_csv(os.path.join(output_path, "client.csv"), index=False)

    # ----------- campaign.csv -----------
    df_campaign = df_total[[
        "client_id", "number_contacts", "contact_duration",
        "previous_campaign_contacts", "previous_outcome",
        "campaign_outcome", "day", "month"
    ]].copy()

    df_campaign["previous_outcome"] = df_campaign["previous_outcome"].apply(
        lambda x: 1 if str(x).lower() == "success" else 0
    )
    df_campaign["campaign_outcome"] = df_campaign["campaign_outcome"].apply(
        lambda x: 1 if str(x).lower() == "yes" else 0
    )

    # Crear columna last_contact_date (YYYY-MM-DD)
    meses = {
        "jan": "01", "feb": "02", "mar": "03", "apr": "04",
        "may": "05", "jun": "06", "jul": "07", "aug": "08",
        "sep": "09", "oct": "10", "nov": "11", "dec": "12"
    }

    def formatear_fecha(row):
        mes = meses.get(str(row["month"]).strip().lower(), "01")
        dia = int(row["day"])
        return f"2022-{mes}-{dia:02d}"

    df_campaign["last_contact_date"] = df_campaign.apply(formatear_fecha, axis=1)
    df_campaign.drop(columns=["day", "month"], inplace=True)

    df_campaign.to_csv(os.path.join(output_path, "campaign.csv"), index=False)

    # ----------- economics.csv -----------
    df_economics = df_total[[
        "client_id", "cons_price_idx", "euribor_three_months"
    ]].copy()

    df_economics.to_csv(os.path.join(output_path, "economics.csv"), index=False)

"""
    En esta tarea se le pide que limpie los datos de una campaña de
    marketing realizada por un banco, la cual tiene como fin la
    recolección de datos de clientes para ofrecerls un préstamo.

    La información recolectada se encuentra en la carpeta
    files/input/ en varios archivos csv.zip comprimidos para ahorrar
    espacio en disco.

    Usted debe procesar directamente los archivos comprimidos (sin
    descomprimirlos). Se desea partir la data en tres archivos csv
    (sin comprimir): client.csv, campaign.csv y economics.csv.
    Cada archivo debe tener las columnas indicadas.

    Los tres archivos generados se almacenarán en la carpeta files/output/.

    client.csv:
    - client_id
    - age
    - job: se debe cambiar el "." por "" y el "-" por "_"
    - marital
    - education: se debe cambiar "." por "_" y "unknown" por pd.NA
    - credit_default: convertir a "yes" a 1 y cualquier otro valor a 0
    - mortage: convertir a "yes" a 1 y cualquier otro valor a 0

    campaign.csv:
    - client_id
    - number_contacts
    - contact_duration
    - previous_campaing_contacts
    - previous_outcome: cmabiar "success" por 1, y cualquier otro valor a 0
    - campaign_outcome: cambiar "yes" por 1 y cualquier otro valor a 0
    - last_contact_day: crear un valor con el formato "YYYY-MM-DD",
        combinando los campos "day" y "month" con el año 2022.

    economics.csv:
    - client_id
    - const_price_idx
    - eurobor_three_months



"""
if __name__ == "__main__":
    clean_campaign_data()
