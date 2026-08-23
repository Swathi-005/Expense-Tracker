import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px
from datetime import datetime


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Expense Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# RESPONSIVE + DARK MODE CSS
# ============================================================

st.markdown("""
<style>

/* Base */
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
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] div {
    color: #FFFFFF !important;
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

.section-title {
    font-size: 24px;
    font-weight: 700;
    color: var(--text-color);
}

/* Login */
.login-box {
    background-color: var(--secondary-background-color);
    padding: 35px;
    border-radius: 20px;
    border: 1px solid rgba(128,128,128,0.30);
    box-shadow: 0 4px 20px rgba(0,0,0,0.10);
    text-align: center;
}

.login-title {
    font-size: 42px;
    font-weight: 700;
    color: var(--text-color);
}

.login-subtitle {
    font-size: 16px;
    color: var(--text-color);
    opacity: 0.75;
    margin-top: 10px;
}

/* Dashboard cards */
.metric-card {
    background-color: var(--secondary-background-color);
    padding: 22px;
    border-radius: 16px;
    border: 1px solid rgba(128,128,128,0.30);
    box-shadow: 0 3px 12px rgba(0,0,0,0.08);
    min-height: 110px;
}

.metric-title {
    color: var(--text-color);
    opacity: 0.75;
    font-size: 15px;
    margin-bottom: 8px;
}

.metric-value {
    font-size: 28px;
    font-weight: 700;
}

/* Inputs */
[data-testid="stWidgetLabel"] p {
    color: var(--text-color) !important;
}

input,
textarea {
    color: var(--text-color) !important;
}

[data-baseweb="select"] * {
    color: var(--text-color) !important;
}

button[data-baseweb="tab"] {
    color: var(--text-color) !important;
}

[data-testid="stMetricLabel"],
[data-testid="stMetricValue"] {
    color: var(--text-color) !important;
}

[data-testid="stVerticalBlockBorderWrapper"] {
    border-color: rgba(128,128,128,0.30) !important;
}

/* Expense card */
.expense-card-title {
    font-size: 18px;
    font-weight: 700;
    color: var(--text-color);
    margin-bottom: 10px;
}

.expense-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 14px;
}

.expense-label {
    opacity: 0.65;
    font-size: 13px;
    color: var(--text-color);
}

.expense-value {
    font-weight: 700;
    font-size: 16px;
    color: var(--text-color);
}

/* Buttons */
.stButton > button {
    border-radius: 8px;
}

hr {
    border-color: rgba(128,128,128,0.25);
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

    .section-title {
        font-size: 20px;
    }

    .login-title {
        font-size: 30px;
    }

    .login-box {
        padding: 22px;
    }

    .metric-card {
        padding: 16px;
        min-height: 90px;
    }

    .metric-value {
        font-size: 22px;
    }

    .expense-grid {
        grid-template-columns: 1fr;
        gap: 10px;
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
# AUTH CLIENT
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
# AUTH PAGE
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
                        "Password must be at least 6 characters."
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
                                    "Account created. "
                                    "Check your email to confirm your account."
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
# USER
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

metadata = (
    st.session_state.user.user_metadata
    or {}
)

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

    c1, c2, c3 = st.columns(3)

    with c1:

        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">
                    💰 Total Expenses
                </div>
                <div class="metric-value"
                style="color:#22C55E;">
                    ₹{total:,.2f}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:

        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">
                    🧾 Transactions
                </div>
                <div class="metric-value"
                style="color:#3B82F6;">
                    {count}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c3:

        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">
                    📈 Average Expense
                </div>
                <div class="metric-value"
                style="color:#A855F7;">
                    ₹{average:,.2f}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.write("")
    st.write("")

    st.markdown(
        '<div class="section-title">🧾 Recent Expenses</div>',
        unsafe_allow_html=True
    )

    st.write("")

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

                st.markdown(
                    f"""
                    <div class="expense-card-title">
                        Expense #{display_id}
                    </div>

                    <div class="expense-grid">

                        <div>
                            <div class="expense-label">
                                Amount
                            </div>
                            <div class="expense-value">
                                ₹{float(row["amount"]):,.2f}
                            </div>
                        </div>

                        <div>
                            <div class="expense-label">
                                Category
                            </div>
                            <div class="expense-value">
                                {row["category"]}
                            </div>
                        </div>

                        <div>
                            <div class="expense-label">
                                Description
                            </div>
                            <div class="expense-value">
                                {row["description"] or "-"}
                            </div>
                        </div>

                        <div>
                            <div class="expense-label">
                                Date
                            </div>
                            <div class="expense-value">
                                {row["expense_date"]}
                            </div>
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True
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

    # ADD
    with st.container(border=True):

        st.markdown(
            '<div class="section-title">➕ Add New Expense</div>',
            unsafe_allow_html=True
        )

        c1, c2 = st.columns(2)

        with c1:

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

        with c2:

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

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"Could not add expense: {str(e)}"
                    )

    st.write("")

    # SEARCH
    st.markdown(
        '<div class="section-title">🔍 Search Expenses</div>',
        unsafe_allow_html=True
    )

    s1, s2 = st.columns(2)

    with s1:

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
            ]
        )

    with s2:

        search_text = st.text_input(
            "Search Description"
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

    st.markdown(
        '<div class="section-title">📋 Your Expenses</div>',
        unsafe_allow_html=True
    )

    st.write("")

    if len(df) == 0:

        st.info("No expenses found.")

    else:

        for display_id, (_, row) in enumerate(
            df.iterrows(),
            start=1
        ):

            expense_id = int(row["id"])

            with st.container(border=True):

                st.markdown(
                    f"""
                    <div class="expense-card-title">
                        Expense #{display_id}
                    </div>

                    <div class="expense-grid">

                        <div>
                            <div class="expense-label">
                                Amount
                            </div>
                            <div class="expense-value">
                                ₹{float(row["amount"]):,.2f}
                            </div>
                        </div>

                        <div>
                            <div class="expense-label">
                                Category
                            </div>
                            <div class="expense-value">
                                {row["category"]}
                            </div>
                        </div>

                        <div>
                            <div class="expense-label">
                                Description
                            </div>
                            <div class="expense-value">
                                {row["description"] or "-"}
                            </div>
                        </div>

                        <div>
                            <div class="expense-label">
                                Date
                            </div>
                            <div class="expense-value">
                                {row["expense_date"]}
                            </div>
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.write("")

                a1, a2 = st.columns(2)

                with a1:

                    if st.button(
                        "✏️ Edit",
                        key=f"edit_{expense_id}",
                        use_container_width=True
                    ):

                        st.session_state.editing_expense = (
                            expense_id
                        )

                        st.rerun()

                with a2:

                    if st.button(
                        "🗑️ Delete",
                        key=f"delete_{expense_id}",
                        use_container_width=True
                    ):

                        try:

                            delete_expense(
                                expense_id
                            )

                            st.rerun()

                        except Exception as e:

                            st.error(
                                f"Delete failed: {str(e)}"
                            )

    # EDIT
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

                st.markdown(
                    '<div class="section-title">'
                    '✏️ Edit Expense'
                    '</div>',
                    unsafe_allow_html=True
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
                    key=f"edit_desc_{editing_id}"
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

                b1, b2 = st.columns(2)

                with b1:

                    if st.button(
                        "💾 Save Changes",
                        type="primary",
                        use_container_width=True
                    ):

                        update_expense(
                            editing_id,
                            edit_amount,
                            edit_category,
                            edit_description,
                            edit_date
                        )

                        st.session_state.editing_expense = None

                        st.rerun()

                with b2:

                    if st.button(
                        "❌ Cancel",
                        use_container_width=True
                    ):

                        st.session_state.editing_expense = None

                        st.rerun()


# ============================================================
# REPORTS
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

    df["amount"] = df["amount"].astype(float)

    total = df["amount"].sum()
    average = df["amount"].mean()
    highest = df["amount"].max()
    count = len(df)

    m1, m2 = st.columns(2)

    with m1:

        st.metric(
            "💰 Total Spending",
            f"₹{total:,.2f}"
        )

        st.metric(
            "📈 Average Expense",
            f"₹{average:,.2f}"
        )

    with m2:

        st.metric(
            "💳 Highest Expense",
            f"₹{highest:,.2f}"
        )

        st.metric(
            "🧾 Transactions",
            count
        )

    category_data = (
        df.groupby("category")["amount"]
        .sum()
        .reset_index()
    )

    st.subheader("🥧 Expense by Category")

    fig = px.pie(
        category_data,
        names="category",
        values="amount",
        hole=0.4
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.subheader("📊 Category Spending")

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
        plot_bgcolor="rgba(0,0,0,0)"
    )

    st.plotly_chart(
        bar,
        use_container_width=True
    )

    st.subheader("📋 Category Summary")

    summary = category_data.copy()

    summary["Percentage"] = (
        summary["amount"] / total * 100
    )

    summary["Amount"] = (
        summary["amount"]
        .map(lambda x: f"₹{x:,.2f}")
    )

    summary["Percentage"] = (
        summary["Percentage"]
        .map(lambda x: f"{x:.1f}%")
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
# ROUTING
# ============================================================

if st.session_state.page == "Dashboard":

    dashboard_page()

elif st.session_state.page == "Expenses":

    expenses_page()

elif st.session_state.page == "Reports":

    reports_page()
