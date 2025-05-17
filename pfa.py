import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

def connect():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database="Shop"
    )

# Ajouter un produit
def ajouter_produit():
    def enregistrer():
        try:
            id_produit = int(entry_id.get())
            nom = entry_nom.get()
            prix = float(entry_prix.get())
            stock = int(entry_stock.get())
            date = entry_date.get()

            if not nom or not date:
                messagebox.showwarning("Champs manquants", "Tous les champs sont obligatoires.")
                return

            db = connect()
            cursor = db.cursor()
            cursor.execute("INSERT INTO produits (id, nom, prix, stock, date_ajout) VALUES (%s, %s, %s, %s, %s)",
                           (id_produit, nom, prix, stock, date))
            db.commit()
            db.close()
            messagebox.showinfo("Succès", "Produit ajouté avec succès.")
            fenetre.destroy()
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    fenetre = tk.Toplevel()
    fenetre.title("Ajouter un produit")
    fenetre.geometry("400x350")
    fenetre.configure(bg="honeydew")

    tk.Label(fenetre, text="ID du produit :", bg="honeydew").pack()
    entry_id = tk.Entry(fenetre)
    entry_id.pack()

    tk.Label(fenetre, text="Nom du produit :", bg="honeydew").pack()
    entry_nom = tk.Entry(fenetre)
    entry_nom.pack()

    tk.Label(fenetre, text="Prix (TND) :", bg="honeydew").pack()
    entry_prix = tk.Entry(fenetre)
    entry_prix.pack()

    tk.Label(fenetre, text="Stock :", bg="honeydew").pack()
    entry_stock = tk.Entry(fenetre)
    entry_stock.pack()

    tk.Label(fenetre, text="Date (AAAA-MM-JJ) :", bg="honeydew").pack()
    entry_date = tk.Entry(fenetre)
    entry_date.pack()

    tk.Button(fenetre, text="Enregistrer", command=enregistrer, bg="green", fg="white").pack(pady=10)

# Voir les produits
def voir_produits():
    fenetre = tk.Toplevel()
    fenetre.title("Produits")
    fenetre.geometry("600x400")
    fenetre.configure(bg="ghost white")

    tree = ttk.Treeview(fenetre, columns=("ID", "Nom", "Prix", "Stock", "Date"), show="headings")
    for col in tree["columns"]:
        tree.heading(col, text=col)
    tree.pack(expand=True, fill="both")

    try:
        db = connect()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM produits")
        for row in cursor.fetchall():
            tree.insert("", tk.END, values=row)
        db.close()
    except Exception as e:
        messagebox.showerror("Erreur", str(e))

# Supprimer un produit
def supprimer_produit():
    def supprimer():
        try:
            produit_id = int(entry_id.get())
            db = connect()
            cursor = db.cursor()
            cursor.execute("DELETE FROM produits WHERE id = %s", (produit_id,))
            db.commit()
            db.close()
            messagebox.showinfo("Succès", "Produit supprimé.")
            fenetre.destroy()
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    fenetre = tk.Toplevel()
    fenetre.title("Supprimer un produit")
    fenetre.geometry("300x150")
    fenetre.configure(bg="misty rose")

    tk.Label(fenetre, text="ID du produit :", bg="misty rose").pack(pady=5)
    entry_id = tk.Entry(fenetre)
    entry_id.pack()

    tk.Button(fenetre, text="Supprimer", command=supprimer, bg="red", fg="white").pack(pady=10)

# Générer la facture
def generer_facture():
    def ajouter_produit_facture():
        try:
            id_produit = int(entry_id.get())
            quantite = int(entry_quantite.get())

            db = connect()
            cursor = db.cursor()
            cursor.execute("SELECT nom, prix, stock FROM produits WHERE id = %s", (id_produit,))
            resultat = cursor.fetchone()

            if not resultat:
                messagebox.showerror("Erreur", "Produit non trouvé.")
                return

            nom, prix, stock_dispo = resultat

            if quantite > stock_dispo:
                messagebox.showwarning("Stock insuffisant", f"Stock disponible : {stock_dispo}")
                return

            total = prix * quantite
            tree.insert("", tk.END, values=(nom, prix, quantite, total))
            total_facture[0] += total

            label_total.config(text=f"Total général : {total_facture[0]} TND")

            cursor.execute("UPDATE produits SET stock = stock - %s WHERE id = %s", (quantite, id_produit))
            db.commit()
            db.close()

            entry_id.delete(0, tk.END)
            entry_quantite.delete(0, tk.END)

        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    fenetre = tk.Toplevel()
    fenetre.title("Facture")
    fenetre.geometry("700x500")
    fenetre.configure(bg="lavender")

    frame_haut = tk.Frame(fenetre, bg="lavender")
    frame_haut.pack(pady=10)

    tk.Label(frame_haut, text="ID Produit :", bg="lavender").grid(row=0, column=0)
    entry_id = tk.Entry(frame_haut)
    entry_id.grid(row=0, column=1)

    tk.Label(frame_haut, text="Quantité :", bg="lavender").grid(row=0, column=2)
    entry_quantite = tk.Entry(frame_haut)
    entry_quantite.grid(row=0, column=3)

    tk.Button(frame_haut, text="Ajouter à la facture", command=ajouter_produit_facture, bg="dark orange", fg="white").grid(row=0, column=4, padx=10)

    tree = ttk.Treeview(fenetre, columns=("Nom", "Prix", "Quantité", "Total"), show="headings")
    for col in tree["columns"]:
        tree.heading(col, text=col)
    tree.pack(expand=True, fill="both")

    total_facture = [0]
    label_total = tk.Label(fenetre, text="Total général : 0 TND", font=("Arial", 14, "bold"), bg="lavender")
    label_total.pack(pady=10)

# Interface principale avec titre cadré
root = tk.Tk()
root.title("Système de gestion de boutique")
root.geometry("600x550")
root.configure(bg="light steel blue")

# Cadre décoratif pour le titre
cadre_titre = tk.Frame(root, bg="white", bd=4, relief="ridge", padx=10, pady=10)
cadre_titre.pack(pady=20)
label_titre = tk.Label(cadre_titre, text="Système de Gestion de Boutique", font=("Britannic Bold", 24), bg="white", fg="dark blue")
label_titre.pack()

tk.Button(root, text="Ajouter un produit", command=ajouter_produit, font=("Arial Black", 14), bg="medium sea green", fg="white", width=25).pack(pady=10)
tk.Button(root, text="Voir les produits", command=voir_produits, font=("Arial Black", 14), bg="royal blue", fg="white", width=25).pack(pady=10)
tk.Button(root, text="Supprimer un produit", command=supprimer_produit, font=("Arial Black", 14), bg="firebrick", fg="white", width=25).pack(pady=10)
tk.Button(root, text="Générer une facture", command=generer_facture, font=("Arial Black", 14), bg="dark orange", fg="white", width=25).pack(pady=10)

root.mainloop()