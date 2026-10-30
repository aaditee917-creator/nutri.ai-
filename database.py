# ============================================================
# SIGN UP PAGE
# EMAIL + PASSWORD
# ============================================================

@app.route(
    "/signup",
    methods=["GET", "POST"]
)
def signup():

    error = None

    if request.method == "POST":

        # ----------------------------------------------------
        # GET EMAIL AND PASSWORD
        # ----------------------------------------------------

        email = request.form.get(
            "email",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        # ----------------------------------------------------
        # VALIDATE
        # ----------------------------------------------------

        if not email or not password:

            error = "Please enter email and password."

            return render_template(
                "signup.html",
                error=error
            )

        # ----------------------------------------------------
        # SAVE USER
        # ----------------------------------------------------

        try:

            conn = sqlite3.connect(
                "database.db"
            )

            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO login_users_email
                (email, password)
                VALUES (?, ?)
                """,
                (
                    email,
                    password
                )
            )

            conn.commit()
            conn.close()

            # After successful sign up → login page
            return redirect(
                url_for("login")
            )

        except sqlite3.IntegrityError:

            error = "This email is already registered."

        except Exception as e:

            print(
                "Sign up error:",
                e
            )

            error = "Sign up failed. Please try again."

    return render_template(
        "signup.html",
        error=error
    )