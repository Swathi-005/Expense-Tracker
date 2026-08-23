import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px
from datetime import datetime


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
# CSS - DARK/LIGHT MODE FRIENDLY
# ============================================================

st.markdown("""
<style>

.stApp {
    background-color: var(--background-color);
    color: var(--text-color);
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

/* Sidebar */

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

/* Titles */

.main-title {
    font-size: 38px;
    font-weight: 700;
    color: var(--text-color);
    margin-bottom: 5px;
}

.subtitle {
    color: var(--text-color);
    opacity: 0.75;
    font-size: 16px;
    margin-bottom: 20px;
}

/* Login */

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

/* Buttons */

.stButton > button {
    border-radius: 8px;
}

/* Inputs */

[data-testid="stWidgetLabel"] p {
    color: var(--text-color) !important;
}

/* Metrics */

[data-testid="stMetricLabel"],
[data-testid="stMetricValue"] {
    color: var(--text-color) !important;
}

/* Mobile */

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
""", unsafe_allow_html=True)


# ============================================================
# SUPABASE
# ============================================================

@st.cache_resource
def create_supabase_client():

    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]

    return create_client(url, key)


supabase = create_supabase_client()


# ============================================================
# SESSION STATE
# ============================================================

if "access_token" not in st.session_state:
    st.session_state.access_token = None

if "refresh_token" not in st.session_state:
    st.session_state.refresh_token = None

if "user" not in st.session_state:
    st.session_state.user = None

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

if "editing_expense" not in st.session_state:
    st.session_state.editing_expense = None


# ============================================================
# AUTHENTICATED CLIENT
# ============================================================

def get_authenticated_client():

    client = create_supabase_client()

    if (
        st.session_state.access_token
        and st.session_state.refresh_token
    ):

        try:

            client.auth.set_session(
                st.session_state.access_token,
                st.session_state.refresh_token
            )

        except Exception:

            return None

    return client


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
            ["🔐 Login", "📝 Create Account"]
        )

        # LOGIN
        with login_tab:

            st.subheader("Welcome Back")

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
                use_container_width=True
            ):

                if not email or not password:

                    st.warning(
                        "Please enter your email and password."
                    )

                else:

                    try:

                        response = (
                            supabase.auth
                            .sign_in_with_password(
                                {
                                    "email": email,
                                    "password": password
                                }
                            )
                        )

                        if response.user and response.session:

                            st.session_state.user = response.user
                            st.session_state.access_token = (
                                response.session.access_token
                            )
                            st.session_state.refresh_token = (
                                response.session.refresh_token
                            )
                            st.session_state.page = "Dashboard"

                            st.rerun()

                        else:

                            st.error("Login failed.")

                    except Exception as e:

                        st.error(
                            f"Login failed: {str(e)}"
                        )

            st.markdown("---")

            st.subheader("Forgot Password?")

            reset_email = st.text_input(
                "Enter your email",
                key="reset_email"
            )

            if st.button(
                "📧 Send Reset Email",
                use_container_width=True
            ):

                if not reset_email:

                    st.warning(
                        "Please enter your email."
                    )

                else:

                    try:

                        supabase.auth.reset_password_for_email(
                            reset_email
                        )

                        st.success(
                            "Password reset email sent."
                        )

                    except Exception as e:

                        st.error(
                            f"Could not send reset email: {str(e)}"
                        )

        # SIGNUP
        with signup_tab:

            st.subheader("Create Your Account")

            name = st.text_input(
                "Full Name",
                key="signup_name"
            )

            signup_email = st.text_input(
                "Email Address",
                key="signup_email"
            )

            signup_password = st.text_input(
                "Password",
                type="password",
                key="signup_password"
            )

            confirm_password = st.text_input(
                "Confirm Password",
                type="password",
                key="signup_confirm"
            )

            if st.button(
                "📝 Create Account",
                type="primary",
                use_container_width=True
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

                elif signup_password != confirm_password:

                    st.error(
                        "Passwords do not match."
                    )

                else:

                    try:

                        response = (
                            supabase.auth
                            .sign_up(
                                {
                                    "email": signup_email,
                                    "password": signup_password,
                                    "options": {
                                        "data": {
                                            "full_name": name
                                        }
                                    }
                                }
                            )
                        )

                        if response.user:

                            if response.session:

                                st.session_state.user = response.user
                                st.session_state.access_token = (
                                    response.session.access_token
                                )
                                st.session_state.refresh_token = (
                                    response.session.refresh_token
                                )
                                st.session_state.page = "Dashboard"

                                st.rerun()

                            else:

                                st.success(
                                    "Account created successfully."
                                )

                                st.info(
                                    "Please check your email and confirm "
                                    "your account before logging in."
                                )

                    except Exception as e:

                        st.error(
                            f"Sign up failed: {str(e)}"
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


supabase = get_authenticated_client()


if supabase is None:

    st.session_state.access_token = None
    st.session_state.refresh_token = None
    st.session_state.user = None

    st.rerun()


# ============================================================
# CURRENT USER
# ============================================================

try:

    user_response = supabase.auth.get_user()
    current_user = user_response.user

    if current_user is None:
        raise Exception("Session expired.")

    st.session_state.user = current_user

except Exception:

    st.session_state.access_token = None
    st.session_state.refresh_token = None
    st.session_state.user = None

    st.rerun()


user_id = st.session_state.user.id
user_email = st.session_state.user.email

metadata = st.session_state.user.user_metadata or {}

user_name = metadata.get(
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
            "id, amount, category, description, expense_date, created_at"
        )
        .eq("user_id", user_id)
        .order("id", desc=True)
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

    return pd.DataFrame(data)


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
        .eq("id", expense_id)
        .eq("user_id", user_id)
        .execute()
    )


def delete_expense(expense_id):

    (
        supabase
        .table("expenses")
        .delete()
        .eq("id", expense_id)
        .eq("user_id", user_id)
        .execute()
    )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div style="text-align:center;">
            <div style="
                font-size:30px;
                font-weight:700;
                color:white;
            ">
                💰 Expense Tracker
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    st.write(
        f"👋 Hello, **{user_name}**"
    )

    st.caption(user_email)

    st.markdown("---")

    if st.button(
        "🏠 Dashboard",
        use_container_width=True
    ):

        st.session_state.page = "Dashboard"
        st.rerun()

    if st.button(
        "💳 Expenses",
        use_container_width=True
    ):

        st.session_state.page = "Expenses"
        st.rerun()

    if st.button(
        "📊 Reports",
        use_container_width=True
    ):

        st.session_state.page = "Reports"
        st.rerun()

    st.markdown("---")

    if st.button(
        "🚪 Logout",
        use_container_width=True
    ):

        try:
            supabase.auth.sign_out()
        except Exception:
            pass

        st.session_state.access_token = None
        st.session_state.refresh_token = None
        st.session_state.user = None
        st.session_state.page = "Dashboard"

        st.rerun()


# ============================================================
# DASHBOARD
# ============================================================

def dashboard_page():

    df = get_expenses()

    st.markdown(
        '<div class="main-title">Expense Dashboard</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f'<div class="subtitle">'
        f'Welcome back, {user_name} 👋'
        f'</div>',
        unsafe_allow_html=True
    )

    if len(df) > 0:

        df["amount"] = df["amount"].astype(float)

        total = df["amount"].sum()
        count = len(df)
        average = total / count

    else:

        total = 0
        count = 0
        average = 0

    # Native Streamlit metrics
    col1, col2, col3 = st.columns(3)

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
    st.subheader("🧾 Recent Expenses")

    if len(df) == 0:

        st.info(
            "You haven't added any expenses yet."
        )

    else:

        for display_id, (_, row) in enumerate(
            df.head(5).iterrows(),
            start=1
        ):

            with st.container(border=True):

                st.subheader(
                    f"Expense #{display_id}"
                )

                st.write(
                    f"💰 **Amount:** ₹{float(row['amount']):,.2f}"
                )

                st.write(
                    f"🏷️ **Category:** {row['category']}"
                )

                st.write(
                    f"📝 **Description:** {row['description'] or '-'}"
                )

                st.write(
                    f"📅 **Date:** {row['expense_date']}"
                )


# ============================================================
# EXPENSES PAGE
# ============================================================

def expenses_page():

    st.markdown(
        '<div class="main-title">Expense Management</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        'Add, edit, delete and search your expenses.'
        '</div>',
        unsafe_allow_html=True
    )

    # ========================================================
    # ADD EXPENSE
    # ========================================================

    with st.container(border=True):

        st.subheader(
            "➕ Add New Expense"
        )

        col1, col2 = st.columns(2)

        with col1:

            amount = st.number_input(
                "Amount",
                min_value=0.0,
                step=100.0,
                format="%.2f"
            )

            category = st.selectbox(
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

        with col2:

            description = st.text_input(
                "Description",
                placeholder="What was this expense for?"
            )

            expense_date = st.date_input(
                "Date",
                value=datetime.now().date()
            )

        if st.button(
            "💾 Add Expense",
            type="primary",
            use_container_width=True
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
                        "Expense added successfully!"
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"Could not add expense: {str(e)}"
                    )

    st.write("")

    # ========================================================
    # SEARCH
    # ========================================================

    st.subheader(
        "🔍 Search Expenses"
    )

    search_col1, search_col2 = st.columns(2)

    with search_col1:

        search_category = st.selectbox(
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

    with search_col2:

        search_text = st.text_input(
            "Search Description",
            placeholder="Type description...",
            key="search_text"
        )

    df = get_expenses()

    if search_category != "All":

        df = df[
            df["category"] == search_category
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

    st.write("")

    # ========================================================
    # EXPENSE LIST
    # ========================================================

    st.subheader(
        "📋 Your Expenses"
    )

    if len(df) == 0:

        st.info(
            "No expenses found."
        )

    else:

        for display_id, (_, row) in enumerate(
            df.iterrows(),
            start=1
        ):

            expense_id = int(row["id"])

            amount_value = float(row["amount"])
            category_value = row["category"]
            description_value = row["description"] or "-"
            date_value = row["expense_date"]

            with st.container(border=True):

                st.subheader(
                    f"Expense #{display_id}"
                )

                st.write(
                    f"💰 **Amount:** ₹{amount_value:,.2f}"
                )

                st.write(
                    f"🏷️ **Category:** {category_value}"
                )

                st.write(
                    f"📝 **Description:** {description_value}"
                )

                st.write(
                    f"📅 **Date:** {date_value}"
                )

                edit_col, delete_col = st.columns(2)

                with edit_col:

                    if st.button(
                        "✏️ Edit",
                        key=f"edit_{expense_id}",
                        use_container_width=True
                    ):

                        st.session_state.editing_expense = (
                            expense_id
                        )

                        st.rerun()

                with delete_col:

                    if st.button(
                        "🗑️ Delete",
                        key=f"delete_{expense_id}",
                        use_container_width=True
                    ):

                        try:

                            delete_expense(
                                expense_id
                            )

                            st.success(
                                "Expense deleted successfully!"
                            )

                            st.rerun()

                        except Exception as e:

                            st.error(
                                f"Delete failed: {str(e)}"
                            )

    # ========================================================
    # EDIT EXPENSE
    # ========================================================

    editing_id = st.session_state.editing_expense

    if editing_id is not None:

        all_expenses = get_expenses()

        selected = all_expenses[
            all_expenses["id"] == editing_id
        ]

        if len(selected) > 0:

            row = selected.iloc[0]

            st.write("")

            with st.container(border=True):

                st.subheader(
                    "✏️ Edit Expense"
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

                current_category = row["category"]

                if current_category in categories:
                    current_index = categories.index(
                        current_category
                    )
                else:
                    current_index = 0

                edit_amount = st.number_input(
                    "Amount",
                    value=float(row["amount"]),
                    min_value=0.0,
                    step=100.0,
                    format="%.2f",
                    key=f"edit_amount_{editing_id}"
                )

                edit_category = st.selectbox(
                    "Category",
                    categories,
                    index=current_index,
                    key=f"edit_category_{editing_id}"
                )

                edit_description = st.text_input(
                    "Description",
                    value=row["description"] or "",
                    key=f"edit_description_{editing_id}"
                )

                try:

                    current_date = datetime.strptime(
                        str(row["expense_date"]),
                        "%Y-%m-%d"
                    ).date()

                except Exception:

                    current_date = datetime.now().date()

                edit_date = st.date_input(
                    "Date",
                    value=current_date,
                    key=f"edit_date_{editing_id}"
                )

                save_col, cancel_col = st.columns(2)

                with save_col:

                    if st.button(
                        "💾 Save Changes",
                        type="primary",
                        use_container_width=True
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
                                    "Expense updated successfully!"
                                )

                                st.rerun()

                            except Exception as e:

                                st.error(
                                    f"Update failed: {str(e)}"
                                )

                with cancel_col:

                    if st.button(
                        "❌ Cancel",
                        use_container_width=True
                    ):

                        st.session_state.editing_expense = None

                        st.rerun()


# ============================================================
# REPORTS PAGE
# ============================================================

def reports_page():

    st.markdown(
        '<div class="main-title">📊 Reports & Analytics</div>',
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
        df["amount"].astype(float)
    )

    total = df["amount"].sum()
    average = df["amount"].mean()
    highest = df["amount"].max()
    count = len(df)

    # Summary
    col1, col2 = st.columns(2)

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

    st.write("")

    category_data = (
        df
        .groupby("category")["amount"]
        .sum()
        .reset_index()
    )

    # PIE CHART
    st.subheader(
        "🥧 Expense by Category"
    )

    pie_fig = px.pie(
        category_data,
        names="category",
        values="amount",
        hole=0.4
    )

    pie_fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    st.plotly_chart(
        pie_fig,
        use_container_width=True
    )

    # BAR CHART
    st.subheader(
        "📊 Category Spending"
    )

    bar_fig = px.bar(
        category_data,
        x="category",
        y="amount",
        text="amount"
    )

    bar_fig.update_traces(
        texttemplate="₹%{text:.0f}",
        textposition="outside"
    )

    bar_fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Category",
        yaxis_title="Amount"
    )

    st.plotly_chart(
        bar_fig,
        use_container_width=True
    )

    # CATEGORY SUMMARY
    st.subheader(
        "📋 Category Summary"
    )

    summary = category_data.copy()

    summary["Percentage"] = (
        summary["amount"]
        / total
        * 100
    )

    summary["Amount"] = (
        summary["amount"]
        .map(
            lambda x: f"₹{x:,.2f}"
        )
    )

    summary["Percentage"] = (
        summary["Percentage"]
        .map(
            lambda x: f"{x:.1f}%"
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
        use_container_width=True,
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
