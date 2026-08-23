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
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>
.stApp {
    background-color: #F5F7FB;
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

[data-testid="stSidebar"] {
    background-color: #1E293B;
}

[data-testid="stSidebar"] * {
    color: white !important;
}

.main-title {
    font-size: 38px;
    font-weight: 700;
    color: #1E293B;
    margin-bottom: 5px;
}

.subtitle {
    color: #64748B;
    font-size: 16px;
    margin-bottom: 20px;
}

.metric-card {
    background-color: white;
    padding: 22px;
    border-radius: 16px;
    border: 1px solid #E2E8F0;
    box-shadow: 0 3px 12px rgba(0,0,0,0.05);
    min-height: 110px;
}

.metric-title {
    color: #64748B;
    font-size: 15px;
    margin-bottom: 8px;
}

.metric-value {
    font-size: 28px;
    font-weight: 700;
}

.login-box {
    background-color: white;
    padding: 35px;
    border-radius: 20px;
    border: 1px solid #E2E8F0;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    text-align: center;
}

.login-title {
    font-size: 42px;
    font-weight: 700;
    color: #1E293B;
}

.login-subtitle {
    font-size: 16px;
    color: #64748B;
    margin-top: 10px;
}

.section-title {
    font-size: 24px;
    font-weight: 700;
    color: #1E293B;
}

.small-text {
    color: #64748B;
    font-size: 14px;
}

button {
    border-radius: 8px !important;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# SUPABASE CONNECTION
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
    st.write("")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:

        # IMPORTANT:
        # No blank lines inside the HTML block.
        # This prevents HTML from appearing as text.

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


        # ====================================================
        # LOGIN
        # ====================================================

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

            st.write("")

            if st.button(
                "🔑 Login",
                use_container_width=True,
                type="primary"
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

                            st.success(
                                "Login successful!"
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


            st.markdown("---")

            st.subheader("Forgot Password?")

            reset_email = st.text_input(
                "Enter your email",
                placeholder="example@gmail.com",
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
                            "Password reset email sent. "
                            "Please check your inbox."
                        )

                    except Exception as e:

                        st.error(
                            f"Could not send email: {str(e)}"
                        )


        # ====================================================
        # CREATE ACCOUNT
        # ====================================================

        with signup_tab:

            st.subheader("Create Your Account")

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

            confirm_password = st.text_input(
                "Confirm Password",
                type="password",
                placeholder="Re-enter your password",
                key="signup_confirm"
            )

            st.write("")

            if st.button(
                "📝 Create Account",
                use_container_width=True,
                type="primary"
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

                                st.session_state.user = (
                                    response.user
                                )

                                st.session_state.access_token = (
                                    response.session.access_token
                                )

                                st.session_state.refresh_token = (
                                    response.session.refresh_token
                                )

                                st.session_state.page = "Dashboard"

                                st.success(
                                    "Account created successfully!"
                                )

                                st.rerun()

                            else:

                                st.success(
                                    "Account created successfully!"
                                )

                                st.info(
                                    "Please check your email and "
                                    "confirm your account before logging in."
                                )

                        else:

                            st.error(
                                "Account could not be created."
                            )

                    except Exception as e:

                        st.error(
                            f"Sign up failed: {str(e)}"
                        )


# ============================================================
# CHECK LOGIN
# ============================================================

if (
    st.session_state.access_token is None
    or st.session_state.refresh_token is None
):

    authentication_page()

    st.stop()


# ============================================================
# GET AUTHENTICATED CLIENT
# ============================================================

supabase = get_authenticated_client()


if supabase is None:

    st.session_state.access_token = None
    st.session_state.refresh_token = None
    st.session_state.user = None

    st.rerun()


# ============================================================
# GET CURRENT USER
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


# ============================================================
# USER INFORMATION
# ============================================================

user_id = st.session_state.user.id

user_email = st.session_state.user.email

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
            "id, amount, category, description, expense_date, created_at"
        )
        .eq("user_id", user_id)
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

    return pd.DataFrame(data)


def add_expense(
    amount,
    category,
    description,
    expense_date
):

    data = {
        "user_id": user_id,
        "amount": float(amount),
        "category": category,
        "description": description,
        "expense_date": str(expense_date)
    }

    (
        supabase
        .table("expenses")
        .insert(data)
        .execute()
    )


def update_expense(
    expense_id,
    amount,
    category,
    description,
    expense_date
):

    data = {
        "amount": float(amount),
        "category": category,
        "description": description,
        "expense_date": str(expense_date)
    }

    (
        supabase
        .table("expenses")
        .update(data)
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
            <div style="font-size:32px;font-weight:700;">
                💰 Expense
            </div>
            <div style="font-size:32px;font-weight:700;">
                Tracker
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("")

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

        except:

            pass

        st.session_state.access_token = None
        st.session_state.refresh_token = None
        st.session_state.user = None
        st.session_state.page = "Dashboard"

        st.rerun()


# ============================================================
# DASHBOARD PAGE
# ============================================================

def dashboard_page():

    df = get_expenses()

    st.markdown(
        '<div class="main-title">Expense Dashboard</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f'<div class="subtitle">Welcome back, {user_name} 👋</div>',
        unsafe_allow_html=True
    )

    st.write("")


    if len(df) > 0:

        total = df["amount"].astype(float).sum()

        transaction_count = len(df)

        average = total / transaction_count

    else:

        total = 0

        transaction_count = 0

        average = 0


    # ========================================================
    # METRIC CARDS
    # ========================================================

    col1, col2, col3 = st.columns(3)


    with col1:

        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">
                    💰 Total Expenses
                </div>
                <div class="metric-value"
                     style="color:#16A34A;">
                    ₹{total:,.2f}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


    with col2:

        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">
                    🧾 Transactions
                </div>
                <div class="metric-value"
                     style="color:#2563EB;">
                    {transaction_count}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


    with col3:

        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">
                    📈 Average Expense
                </div>
                <div class="metric-value"
                     style="color:#7C3AED;">
                    ₹{average:,.2f}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


    st.write("")
    st.write("")


    # ========================================================
    # RECENT EXPENSES
    # ========================================================

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

        recent_df = df.head(10).copy()

        recent_df["amount"] = (
            recent_df["amount"]
            .astype(float)
            .map(lambda x: f"₹{x:,.2f}")
        )

        recent_df = recent_df[
            [
                "id",
                "amount",
                "category",
                "description",
                "expense_date"
            ]
        ]

        recent_df.columns = [
            "ID",
            "Amount",
            "Category",
            "Description",
            "Date"
        ]

        st.dataframe(
            recent_df,
            use_container_width=True,
            hide_index=True
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

    st.write("")


    # ========================================================
    # ADD EXPENSE
    # ========================================================

    with st.container(border=True):

        st.markdown(
            '<div class="section-title">➕ Add New Expense</div>',
            unsafe_allow_html=True
        )

        st.write("")


        col1, col2, col3, col4 = st.columns(4)


        with col1:

            amount = st.number_input(
                "Amount",
                min_value=0.0,
                step=100.0,
                format="%.2f"
            )


        with col2:

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


        with col3:

            description = st.text_input(
                "Description",
                placeholder="What was this expense for?"
            )


        with col4:

            expense_date = st.date_input(
                "Date",
                value=datetime.now().date()
            )


        st.write("")


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

    st.markdown(
        '<div class="section-title">🔍 Search Expenses</div>',
        unsafe_allow_html=True
    )

    st.write("")


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
            ]
        )


    with search_col2:

        search_text = st.text_input(
            "Search Description",
            placeholder="Search description..."
        )


    st.write("")


    # ========================================================
    # GET DATA
    # ========================================================

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


    st.markdown(
        '<div class="section-title">📋 Your Expenses</div>',
        unsafe_allow_html=True
    )

    st.write("")


    if len(df) == 0:

        st.info(
            "No expenses found."
        )

    else:

        # ====================================================
        # TABLE HEADER
        # ====================================================

        header = st.columns(
            [0.5, 1.2, 1.3, 2.2, 1.3, 1.2]
        )

        header[0].markdown("**#**")
        header[1].markdown("**Amount**")
        header[2].markdown("**Category**")
        header[3].markdown("**Description**")
        header[4].markdown("**Date**")
        header[5].markdown("**Actions**")


        st.divider()


        # ====================================================
        # EXPENSE ROWS
        # ====================================================

        for display_id, (_, row) in enumerate(
            df.iterrows(),
            start=1
        ):

            expense_id = int(row["id"])

            amount_value = float(row["amount"])

            category_value = row["category"]

            description_value = (
                row["description"]
                if row["description"]
                else "-"
            )

            date_value = row["expense_date"]


            row_cols = st.columns(
                [0.5, 1.2, 1.3, 2.2, 1.3, 1.2]
            )


            with row_cols[0]:

                st.write(
                    f"**{display_id}**"
                )


            with row_cols[1]:

                st.write(
                    f"₹{amount_value:,.2f}"
                )


            with row_cols[2]:

                st.write(
                    category_value
                )


            with row_cols[3]:

                st.write(
                    description_value
                )


            with row_cols[4]:

                st.write(
                    date_value
                )


            with row_cols[5]:

                edit_col, delete_col = st.columns(2)


                with edit_col:

                    if st.button(
                        "✏️",
                        key=f"edit_{expense_id}"
                    ):

                        st.session_state.editing_expense = (
                            expense_id
                        )

                        st.rerun()


                with delete_col:

                    if st.button(
                        "🗑️",
                        key=f"delete_{expense_id}"
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


            st.divider()


    # ========================================================
    # EDIT EXPENSE
    # ========================================================

    editing_id = (
        st.session_state.editing_expense
    )


    if editing_id is not None:

        all_expenses = get_expenses()

        selected = all_expenses[
            all_expenses["id"] == editing_id
        ]


        if len(selected) > 0:

            row = selected.iloc[0]


            st.write("")
            st.write("")


            with st.container(border=True):

                st.markdown(
                    '<div class="section-title">'
                    '✏️ Edit Expense'
                    '</div>',
                    unsafe_allow_html=True
                )

                st.write("")


                edit_col1, edit_col2 = st.columns(2)


                with edit_col1:

                    edit_amount = st.number_input(
                        "Amount",
                        min_value=0.0,
                        value=float(row["amount"]),
                        step=100.0,
                        format="%.2f",
                        key=f"edit_amount_{editing_id}"
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

                        category_index = categories.index(
                            current_category
                        )

                    else:

                        category_index = 0


                    edit_category = st.selectbox(
                        "Category",
                        categories,
                        index=category_index,
                        key=f"edit_category_{editing_id}"
                    )


                with edit_col2:

                    edit_description = st.text_input(
                        "Description",
                        value=row["description"] or "",
                        key=f"edit_description_{editing_id}"
                    )


                    try:

                        edit_date = datetime.strptime(
                            str(row["expense_date"]),
                            "%Y-%m-%d"
                        ).date()

                    except:

                        edit_date = datetime.now().date()


                    edit_date = st.date_input(
                        "Date",
                        value=edit_date,
                        key=f"edit_date_{editing_id}"
                    )


                st.write("")


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

    st.write("")


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


    total = df["amount"].sum()

    highest = df["amount"].max()

    transaction_count = len(df)

    average = df["amount"].mean()


    # ========================================================
    # SUMMARY
    # ========================================================

    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.metric(
            "💰 Total Spending",
            f"₹{total:,.2f}"
        )


    with col2:

        st.metric(
            "📈 Average",
            f"₹{average:,.2f}"
        )


    with col3:

        st.metric(
            "💳 Highest Expense",
            f"₹{highest:,.2f}"
        )


    with col4:

        st.metric(
            "🧾 Transactions",
            transaction_count
        )


    st.write("")
    st.write("")


    # ========================================================
    # CATEGORY DATA
    # ========================================================

    category_data = (
        df
        .groupby("category")["amount"]
        .sum()
        .reset_index()
    )


    chart_col1, chart_col2 = st.columns(2)


    # ========================================================
    # PIE CHART
    # ========================================================

    with chart_col1:

        st.subheader(
            "🥧 Expense by Category"
        )


        fig = px.pie(
            category_data,
            names="category",
            values="amount",
            hole=0.4
        )


        fig.update_layout(
            margin=dict(
                t=30,
                b=10,
                l=10,
                r=10
            )
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # ========================================================
    # BAR CHART
    # ========================================================

    with chart_col2:

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
            xaxis_title="Category",
            yaxis_title="Amount"
        )


        st.plotly_chart(
            bar_fig,
            use_container_width=True
        )


    # ========================================================
    # CATEGORY SUMMARY
    # ========================================================

    st.subheader(
        "📋 Category Summary"
    )


    summary = (
        df
        .groupby("category")["amount"]
        .sum()
        .reset_index()
    )


    summary["Percentage"] = (
        summary["amount"]
        / total
        * 100
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
# PAGE ROUTING
# ============================================================

if st.session_state.page == "Dashboard":

    dashboard_page()


elif st.session_state.page == "Expenses":

    expenses_page()


elif st.session_state.page == "Reports":

    reports_page()