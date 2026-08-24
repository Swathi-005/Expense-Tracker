import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px
from datetime import datetime


# ============================================================
# APP URL
# ============================================================

APP_URL = "https://expense-tracker-ghpfs33yfc5qwpkn3mwhti.streamlit.app"


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Expense Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background-color: var(--background-color);
        color: var(--text-color);
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    [data-testid="stSidebar"] {
        background-color: #1E293B;
    }

    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: white !important;
    }

    .main-title {
        font-size: 38px;
        font-weight: 700;
        color: var(--text-color);
        margin-bottom: 5px;
    }

    .subtitle {
        font-size: 16px;
        color: var(--text-color);
        opacity: 0.75;
        margin-bottom: 20px;
    }

    .login-box {
        background-color: var(--secondary-background-color);
        padding: 30px;
        border-radius: 20px;
        border: 1px solid rgba(128,128,128,0.30);
        box-shadow: 0 4px 20px rgba(0,0,0,0.10);
        text-align: center;
    }

    .login-title {
        font-size: 40px;
        font-weight: 700;
        color: var(--text-color);
    }

    .login-subtitle {
        font-size: 16px;
        color: var(--text-color);
        opacity: 0.75;
        margin-top: 8px;
    }

    [data-testid="stMetricLabel"],
    [data-testid="stMetricValue"] {
        color: var(--text-color) !important;
    }

    [data-testid="stWidgetLabel"] p {
        color: var(--text-color) !important;
    }

    .stButton > button {
        border-radius: 8px;
    }

    @media (max-width: 768px) {

        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }

        .main-title {
            font-size: 28px;
        }

        .login-title {
            font-size: 30px;
        }

        .login-box {
            padding: 20px;
        }
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SUPABASE CLIENT
# ============================================================

def new_supabase_client():

    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )


# Do NOT cache an authenticated Supabase client.
# Each Streamlit user should have their own session.
supabase = new_supabase_client()


# ============================================================
# SESSION STATE
# ============================================================

defaults = {
    "access_token": None,
    "refresh_token": None,
    "user": None,
    "page": "Dashboard",
    "editing_expense": None,
    "password_recovery": False,
    "reset_complete": False
}

for key, value in defaults.items():

    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# SESSION HELPERS
# ============================================================

def save_auth_session(response):

    if response.user is not None:
        st.session_state.user = response.user

    if response.session is not None:

        st.session_state.access_token = (
            response.session.access_token
        )

        st.session_state.refresh_token = (
            response.session.refresh_token
        )


def clear_auth_session():

    st.session_state.access_token = None
    st.session_state.refresh_token = None
    st.session_state.user = None
    st.session_state.editing_expense = None
    st.session_state.page = "Dashboard"


def get_authenticated_client():

    if (
        not st.session_state.access_token
        or not st.session_state.refresh_token
    ):
        return None

    client = new_supabase_client()

    try:

        response = client.auth.set_session(
            st.session_state.access_token,
            st.session_state.refresh_token
        )

        if response.session:

            st.session_state.access_token = (
                response.session.access_token
            )

            st.session_state.refresh_token = (
                response.session.refresh_token
            )

        return client

    except Exception:

        return None


# ============================================================
# HANDLE PASSWORD RESET LINK
# ============================================================

def handle_recovery_link():

    token_hash = st.query_params.get("token_hash")
    auth_type = st.query_params.get("type")

    if not token_hash:
        return

    if auth_type != "recovery":
        return

    try:

        client = new_supabase_client()

        response = client.auth.verify_otp(
            {
                "token_hash": token_hash,
                "type": "recovery"
            }
        )

        if response.session:

            save_auth_session(response)

            st.session_state.password_recovery = True

            st.query_params.clear()

            st.rerun()

        else:

            st.error(
                "The password reset link is invalid or has expired."
            )

    except Exception as e:

        st.error(
            "The password reset link is invalid or has expired."
        )

        st.caption(str(e))


handle_recovery_link()


# ============================================================
# PASSWORD RESET PAGE
# ============================================================

def password_reset_page():

    st.write("")
    st.write("")

    left, center, right = st.columns([1, 2, 1])

    with center:

        st.title("🔐 Reset Password")

        st.info(
            "Create a new password for your Expense Tracker account."
        )

        new_password = st.text_input(
            "New Password",
            type="password",
            placeholder="Minimum 6 characters",
            key="recovery_new_password"
        )

        confirm_password = st.text_input(
            "Confirm New Password",
            type="password",
            placeholder="Re-enter your password",
            key="recovery_confirm_password"
        )

        if st.button(
            "💾 Update Password",
            type="primary",
            width="stretch"
        ):

            if len(new_password) < 6:

                st.warning(
                    "Password must contain at least 6 characters."
                )

            elif new_password != confirm_password:

                st.error(
                    "Passwords do not match."
                )

            else:

                try:

                    client = get_authenticated_client()

                    if client is None:

                        st.error(
                            "Your password reset session expired. "
                            "Please request another reset link."
                        )

                        return

                    client.auth.update_user(
                        {
                            "password": new_password
                        }
                    )

                    st.session_state.password_recovery = False
                    st.session_state.reset_complete = True

                    clear_auth_session()

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"Password update failed: {str(e)}"
                    )


# ============================================================
# PASSWORD RESET SUCCESS
# ============================================================

def password_reset_success():

    st.write("")
    st.write("")

    left, center, right = st.columns([1, 2, 1])

    with center:

        st.success(
            "✅ Your password has been changed successfully."
        )

        st.info(
            "You can now log in using your new password."
        )

        if st.button(
            "🔐 Go to Login",
            type="primary",
            width="stretch"
        ):

            st.session_state.reset_complete = False

            st.rerun()


if st.session_state.password_recovery:

    password_reset_page()

    st.stop()


if st.session_state.reset_complete:

    password_reset_success()

    st.stop()


# ============================================================
# AUTHENTICATION PAGE
# ============================================================

def authentication_page():

    st.write("")
    st.write("")

    left, center, right = st.columns([1, 2, 1])

    with center:

        st.markdown(
            '<div class="login-box">'
            '<div class="login-title">💰 Expense Tracker</div>'
            '<div class="login-subtitle">'
            'Manage your expenses anywhere, anytime'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )

        st.write("")

        login_tab, signup_tab = st.tabs(
            [
                "🔐 Login",
                "📝 Create Account"
            ]
        )


        # ====================================================
        # LOGIN
        # ====================================================

        with login_tab:

            st.subheader(
                "Welcome Back"
            )

            email = st.text_input(
                "Email Address",
                placeholder="example@gmail.com",
                key="login_email"
            )

            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password",
                key="login_password"
            )

            if st.button(
                "🔑 Login",
                type="primary",
                width="stretch",
                key="login_button"
            ):

                if not email or not password:

                    st.warning(
                        "Please enter your email and password."
                    )

                else:

                    try:

                        client = new_supabase_client()

                        response = (
                            client.auth
                            .sign_in_with_password(
                                {
                                    "email": email,
                                    "password": password
                                }
                            )
                        )

                        if (
                            response.user
                            and response.session
                        ):

                            save_auth_session(
                                response
                            )

                            st.session_state.page = (
                                "Dashboard"
                            )

                            st.rerun()

                        else:

                            st.error(
                                "Login failed."
                            )

                    except Exception as e:

                        st.error(
                            f"Login failed: {str(e)}"
                        )


            # ================================================
            # FORGOT PASSWORD
            # ================================================

            st.markdown("---")

            st.subheader(
                "Forgot Password?"
            )

            st.caption(
                "Enter your registered email address and "
                "we will send you a reset link."
            )

            reset_email = st.text_input(
                "Registered Email",
                placeholder="example@gmail.com",
                key="reset_email"
            )

            if st.button(
                "📧 Send Password Reset Link",
                width="stretch",
                key="send_reset_button"
            ):

                if not reset_email:

                    st.warning(
                        "Please enter your email."
                    )

                else:

                    try:

                        client = new_supabase_client()

                        client.auth.reset_password_for_email(
                            reset_email,
                            {
                                "redirect_to": APP_URL
                            }
                        )

                        st.success(
                            "Password reset email sent."
                        )

                        st.info(
                            "Check your email and click "
                            "'Reset Password'."
                        )

                    except Exception as e:

                        st.error(
                            f"Could not send reset email: {str(e)}"
                        )


        # ====================================================
        # SIGN UP
        # ====================================================

        with signup_tab:

            st.subheader(
                "Create Your Account"
            )

            name = st.text_input(
                "Full Name",
                placeholder="Enter your name",
                key="signup_name"
            )

            signup_email = st.text_input(
                "Email Address",
                placeholder="example@gmail.com",
                key="signup_email"
            )

            signup_password = st.text_input(
                "Password",
                type="password",
                placeholder="Minimum 6 characters",
                key="signup_password"
            )

            signup_confirm = st.text_input(
                "Confirm Password",
                type="password",
                placeholder="Re-enter your password",
                key="signup_confirm"
            )

            if st.button(
                "📝 Create Account",
                type="primary",
                width="stretch",
                key="signup_button"
            ):

                if not name:

                    st.warning(
                        "Please enter your name."
                    )

                elif not signup_email:

                    st.warning(
                        "Please enter your email."
                    )

                elif len(signup_password) < 6:

                    st.warning(
                        "Password must contain at least 6 characters."
                    )

                elif signup_password != signup_confirm:

                    st.error(
                        "Passwords do not match."
                    )

                else:

                    try:

                        client = new_supabase_client()

                        response = client.auth.sign_up(
                            {
                                "email": signup_email,
                                "password": signup_password,
                                "options": {
                                    "data": {
                                        "full_name": name
                                    },
                                    "email_redirect_to": APP_URL
                                }
                            }
                        )

                        if response.user:

                            if response.session:

                                save_auth_session(
                                    response
                                )

                                st.session_state.page = (
                                    "Dashboard"
                                )

                                st.rerun()

                            else:

                                st.success(
                                    "Account created successfully."
                                )

                                st.info(
                                    "Please check your email and click "
                                    "the confirmation link. "
                                    "After confirmation, return here "
                                    "and log in."
                                )

                        else:

                            st.error(
                                "Account could not be created."
                            )

                    except Exception as e:

                        st.error(
                            f"Signup failed: {str(e)}"
                        )


# ============================================================
# LOGIN CHECK
# ============================================================

if (
    st.session_state.access_token is None
    or st.session_state.refresh_token is None
):

    authentication_page()

    st.stop()


# ============================================================
# AUTHENTICATED SUPABASE CLIENT
# ============================================================

supabase = get_authenticated_client()


if supabase is None:

    clear_auth_session()

    st.rerun()


# ============================================================
# GET CURRENT USER
# ============================================================

try:

    response = supabase.auth.get_user()

    current_user = response.user

    if current_user is None:

        raise Exception(
            "Session expired."
        )

    st.session_state.user = (
        current_user
    )

except Exception:

    clear_auth_session()

    st.rerun()


# ============================================================
# USER DETAILS
# ============================================================

user_id = (
    st.session_state.user.id
)

user_email = (
    st.session_state.user.email
)

user_metadata = (
    st.session_state.user.user_metadata
    or {}
)

user_name = user_metadata.get(
    "full_name",
    "User"
)


# ============================================================
# DATABASE FUNCTIONS
# ============================================================

def get_expenses():

    response = (
        supabase
        .table("expenses")
        .select(
            "id, amount, category, "
            "description, expense_date, created_at"
        )
        .eq(
            "user_id",
            user_id
        )
        .order(
            "id",
            desc=True
        )
        .execute()
    )

    data = response.data or []

    if not data:

        return pd.DataFrame(
            columns=[
                "id",
                "amount",
                "category",
                "description",
                "expense_date",
                "created_at"
            ]
        )

    df = pd.DataFrame(data)

    df["id"] = pd.to_numeric(
        df["id"],
        errors="coerce"
    )

    return df


def add_expense(
    amount,
    category,
    description,
    expense_date
):

    (
        supabase
        .table("expenses")
        .insert(
            {
                "user_id": user_id,
                "amount": float(amount),
                "category": category,
                "description": description,
                "expense_date": str(expense_date)
            }
        )
        .execute()
    )


def update_expense(
    expense_id,
    amount,
    category,
    description,
    expense_date
):

    (
        supabase
        .table("expenses")
        .update(
            {
                "amount": float(amount),
                "category": category,
                "description": description,
                "expense_date": str(expense_date)
            }
        )
        .eq(
            "id",
            int(expense_id)
        )
        .eq(
            "user_id",
            user_id
        )
        .execute()
    )


def delete_expense(
    expense_id
):

    (
        supabase
        .table("expenses")
        .delete()
        .eq(
            "id",
            int(expense_id)
        )
        .eq(
            "user_id",
            user_id
        )
        .execute()
    )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div style="
            text-align:center;
            font-size:30px;
            font-weight:700;
            color:white;
        ">
            💰 Expense Tracker
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    st.write(
        f"👋 Hello, **{user_name}**"
    )

    st.caption(
        user_email
    )

    st.markdown("---")

    if st.button(
        "🏠 Dashboard",
        width="stretch"
    ):

        st.session_state.page = (
            "Dashboard"
        )

        st.rerun()


    if st.button(
        "💳 Expenses",
        width="stretch"
    ):

        st.session_state.page = (
            "Expenses"
        )

        st.rerun()


    if st.button(
        "📊 Reports",
        width="stretch"
    ):

        st.session_state.page = (
            "Reports"
        )

        st.rerun()


    st.markdown("---")


    if st.button(
        "🚪 Logout",
        width="stretch"
    ):

        try:

            supabase.auth.sign_out()

        except Exception:

            pass

        clear_auth_session()

        st.rerun()


# ============================================================
# DASHBOARD PAGE
# ============================================================

def dashboard_page():

    df = get_expenses()

    st.markdown(
        '<div class="main-title">'
        'Expense Dashboard'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f'<div class="subtitle">'
        f'Welcome back, {user_name} 👋'
        f'</div>',
        unsafe_allow_html=True
    )


    if len(df) > 0:

        df["amount"] = (
            df["amount"]
            .astype(float)
        )

        total = (
            df["amount"]
            .sum()
        )

        count = len(df)

        average = (
            total / count
        )

    else:

        total = 0
        count = 0
        average = 0


    col1, col2, col3 = (
        st.columns(3)
    )


    with col1:

        st.metric(
            "💰 Total Expenses",
            f"₹{total:,.2f}"
        )


    with col2:

        st.metric(
            "🧾 Transactions",
            count
        )


    with col3:

        st.metric(
            "📈 Average Expense",
            f"₹{average:,.2f}"
        )


    st.write("")

    st.subheader(
        "🧾 Recent Expenses"
    )


    if len(df) == 0:

        st.info(
            "You haven't added any expenses yet."
        )

        return


    for display_id, (_, row) in enumerate(
        df.head(5).iterrows(),
        start=1
    ):

        with st.container(
            border=True
        ):

            st.subheader(
                f"Expense #{display_id}"
            )

            st.write(
                f"💰 **Amount:** "
                f"₹{float(row['amount']):,.2f}"
            )

            st.write(
                f"🏷️ **Category:** "
                f"{row['category']}"
            )

            st.write(
                f"📝 **Description:** "
                f"{row['description'] or '-'}"
            )

            st.write(
                f"📅 **Date:** "
                f"{row['expense_date']}"
            )


# ============================================================
# EXPENSE MANAGEMENT PAGE
# ============================================================

def expenses_page():

    st.markdown(
        '<div class="main-title">'
        'Expense Management'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        'Add, edit, delete and search your expenses.'
        '</div>',
        unsafe_allow_html=True
    )


    # ========================================================
    # EDIT FORM
    # ========================================================

    editing_id = (
        st.session_state.editing_expense
    )


    if editing_id is not None:

        all_expenses = (
            get_expenses()
        )

        selected = all_expenses[
            all_expenses["id"]
            == int(editing_id)
        ]


        if len(selected) > 0:

            row = (
                selected.iloc[0]
            )


            with st.container(
                border=True
            ):

                st.subheader(
                    "✏️ Edit Expense"
                )

                st.info(
                    "Change the details below and "
                    "click Save Changes."
                )


                categories = [
                    "Food",
                    "Travel",
                    "Shopping",
                    "Bills",
                    "Entertainment",
                    "Education",
                    "Health",
                    "Other"
                ]


                current_category = (
                    row["category"]
                )


                if current_category in categories:

                    current_index = (
                        categories.index(
                            current_category
                        )
                    )

                else:

                    current_index = 0


                edit_amount = (
                    st.number_input(
                        "Edit Amount",
                        min_value=0.0,
                        value=float(
                            row["amount"]
                        ),
                        step=100.0,
                        format="%.2f",
                        key=(
                            f"edit_amount_"
                            f"{editing_id}"
                        )
                    )
                )


                edit_category = (
                    st.selectbox(
                        "Edit Category",
                        categories,
                        index=current_index,
                        key=(
                            f"edit_category_"
                            f"{editing_id}"
                        )
                    )
                )


                edit_description = (
                    st.text_input(
                        "Edit Description",
                        value=(
                            row[
                                "description"
                            ]
                            or ""
                        ),
                        key=(
                            f"edit_description_"
                            f"{editing_id}"
                        )
                    )
                )


                try:

                    current_date = (
                        datetime.strptime(
                            str(
                                row[
                                    "expense_date"
                                ]
                            ),
                            "%Y-%m-%d"
                        ).date()
                    )

                except Exception:

                    current_date = (
                        datetime.now()
                        .date()
                    )


                edit_date = (
                    st.date_input(
                        "Edit Date",
                        value=current_date,
                        key=(
                            f"edit_date_"
                            f"{editing_id}"
                        )
                    )
                )


                save_col, cancel_col = (
                    st.columns(2)
                )


                with save_col:

                    if st.button(
                        "💾 Save Changes",
                        type="primary",
                        width="stretch",
                        key=(
                            f"save_"
                            f"{editing_id}"
                        )
                    ):

                        if edit_amount <= 0:

                            st.warning(
                                "Amount must be greater than 0."
                            )

                        else:

                            try:

                                update_expense(
                                    editing_id,
                                    edit_amount,
                                    edit_category,
                                    edit_description,
                                    edit_date
                                )

                                st.session_state.editing_expense = None

                                st.success(
                                    "Expense updated successfully."
                                )

                                st.rerun()

                            except Exception as e:

                                st.error(
                                    f"Update failed: {str(e)}"
                                )


                with cancel_col:

                    if st.button(
                        "❌ Cancel",
                        width="stretch",
                        key=(
                            f"cancel_"
                            f"{editing_id}"
                        )
                    ):

                        st.session_state.editing_expense = None

                        st.rerun()


            st.write("")


    # ========================================================
    # ADD EXPENSE
    # ========================================================

    with st.container(
        border=True
    ):

        st.subheader(
            "➕ Add New Expense"
        )


        col1, col2 = (
            st.columns(2)
        )


        with col1:

            amount = (
                st.number_input(
                    "Amount",
                    min_value=0.0,
                    step=100.0,
                    format="%.2f"
                )
            )


            category = (
                st.selectbox(
                    "Category",
                    [
                        "Food",
                        "Travel",
                        "Shopping",
                        "Bills",
                        "Entertainment",
                        "Education",
                        "Health",
                        "Other"
                    ]
                )
            )


        with col2:

            description = (
                st.text_input(
                    "Description",
                    placeholder=(
                        "What was this expense for?"
                    )
                )
            )


            expense_date = (
                st.date_input(
                    "Date",
                    value=(
                        datetime.now()
                        .date()
                    )
                )
            )


        if st.button(
            "💾 Add Expense",
            type="primary",
            width="stretch",
            key="add_expense"
        ):

            if amount <= 0:

                st.warning(
                    "Please enter an amount greater than 0."
                )

            else:

                try:

                    add_expense(
                        amount,
                        category,
                        description,
                        expense_date
                    )

                    st.success(
                        "Expense added successfully."
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"Could not add expense: {str(e)}"
                    )


    # ========================================================
    # SEARCH
    # ========================================================

    st.write("")

    st.subheader(
        "🔍 Search Expenses"
    )


    search_col1, search_col2 = (
        st.columns(2)
    )


    with search_col1:

        search_category = (
            st.selectbox(
                "Search by Category",
                [
                    "All",
                    "Food",
                    "Travel",
                    "Shopping",
                    "Bills",
                    "Entertainment",
                    "Education",
                    "Health",
                    "Other"
                ],
                key="search_category"
            )
        )


    with search_col2:

        search_text = (
            st.text_input(
                "Search Description",
                placeholder=(
                    "Type description..."
                ),
                key="search_text"
            )
        )


    df = get_expenses()


    if search_category != "All":

        df = df[
            df["category"]
            == search_category
        ]


    if search_text:

        df = df[
            df["description"]
            .fillna("")
            .str.contains(
                search_text,
                case=False,
                na=False
            )
        ]


    # ========================================================
    # EXPENSE LIST
    # ========================================================

    st.write("")

    st.subheader(
        "📋 Your Expenses"
    )


    if len(df) == 0:

        st.info(
            "No expenses found."
        )

        return


    for display_id, (_, row) in enumerate(
        df.iterrows(),
        start=1
    ):

        expense_id = int(
            row["id"]
        )


        with st.container(
            border=True
        ):

            st.subheader(
                f"Expense #{display_id}"
            )

            st.write(
                f"💰 **Amount:** "
                f"₹{float(row['amount']):,.2f}"
            )

            st.write(
                f"🏷️ **Category:** "
                f"{row['category']}"
            )

            st.write(
                f"📝 **Description:** "
                f"{row['description'] or '-'}"
            )

            st.write(
                f"📅 **Date:** "
                f"{row['expense_date']}"
            )


            edit_col, delete_col = (
                st.columns(2)
            )


            with edit_col:

                if st.button(
                    "✏️ Edit",
                    width="stretch",
                    key=(
                        f"edit_"
                        f"{expense_id}"
                    )
                ):

                    st.session_state.editing_expense = (
                        expense_id
                    )

                    st.rerun()


            with delete_col:

                if st.button(
                    "🗑️ Delete",
                    width="stretch",
                    key=(
                        f"delete_"
                        f"{expense_id}"
                    )
                ):

                    try:

                        delete_expense(
                            expense_id
                        )

                        st.success(
                            "Expense deleted successfully."
                        )

                        st.rerun()

                    except Exception as e:

                        st.error(
                            f"Delete failed: {str(e)}"
                        )


# ============================================================
# REPORTS
# ============================================================

def reports_page():

    st.markdown(
        '<div class="main-title">'
        '📊 Reports & Analytics'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        'Understand where your money is going.'
        '</div>',
        unsafe_allow_html=True
    )


    df = get_expenses()


    if len(df) == 0:

        st.info(
            "Add expenses to generate reports."
        )

        return


    df["amount"] = (
        df["amount"]
        .astype(float)
    )


    total = (
        df["amount"]
        .sum()
    )

    average = (
        df["amount"]
        .mean()
    )

    highest = (
        df["amount"]
        .max()
    )

    count = len(df)


    col1, col2 = (
        st.columns(2)
    )


    with col1:

        st.metric(
            "💰 Total Spending",
            f"₹{total:,.2f}"
        )

        st.metric(
            "📈 Average Expense",
            f"₹{average:,.2f}"
        )


    with col2:

        st.metric(
            "💳 Highest Expense",
            f"₹{highest:,.2f}"
        )

        st.metric(
            "🧾 Transactions",
            count
        )


    category_data = (
        df.groupby(
            "category"
        )["amount"]
        .sum()
        .reset_index()
    )


    # ========================================================
    # PIE CHART
    # ========================================================

    st.subheader(
        "🥧 Expense by Category"
    )


    pie = px.pie(
        category_data,
        names="category",
        values="amount",
        hole=0.4
    )


    pie.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )


    st.plotly_chart(
        pie,
        width="stretch"
    )


    # ========================================================
    # BAR CHART
    # ========================================================

    st.subheader(
        "📊 Category Spending"
    )


    bar = px.bar(
        category_data,
        x="category",
        y="amount",
        text="amount"
    )


    bar.update_traces(
        texttemplate="₹%{text:.0f}",
        textposition="outside"
    )


    bar.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Category",
        yaxis_title="Amount"
    )


    st.plotly_chart(
        bar,
        width="stretch"
    )


    # ========================================================
    # CATEGORY SUMMARY
    # ========================================================

    st.subheader(
        "📋 Category Summary"
    )


    summary = (
        category_data.copy()
    )


    summary["Percentage"] = (
        summary["amount"]
        / total
        * 100
    )


    summary["Amount"] = (
        summary["amount"]
        .map(
            lambda value:
            f"₹{value:,.2f}"
        )
    )


    summary["Percentage"] = (
        summary["Percentage"]
        .map(
            lambda value:
            f"{value:.1f}%"
        )
    )


    summary = summary[
        [
            "category",
            "Amount",
            "Percentage"
        ]
    ]


    summary.columns = [
        "Category",
        "Amount",
        "Percentage"
    ]


    st.dataframe(
        summary,
        width="stretch",
        hide_index=True
    )


# ============================================================
# PAGE ROUTING
# ============================================================

if st.session_state.page == "Dashboard":

    dashboard_page()


elif st.session_state.page == "Expenses":

    expenses_page()


elif st.session_state.page == "Reports":

    reports_page()
