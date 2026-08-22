# =============================================================================
# decorators.py
# Backend-enforced role protection. This is what actually stops a "user"
# account from loading the creator/admin dashboards by guessing the URL -
# it does NOT rely on hiding buttons in the frontend.
# =============================================================================
from functools import wraps
from flask import redirect, url_for
from flask_login import current_user


# Where each role gets sent if they try to access a page that isn't theirs.
_OWN_DASHBOARD = {
    "user": "auth.user_dashboard",
    "creator": "auth.creator_dashboard",
    "admin": "auth.admin_dashboard",
}


def role_required(required_role: str):
    """
    Use on any route that should only be reachable by ONE specific role.

    Example:
        @auth_bp.route("/admin/dashboard")
        @login_required
        @role_required("admin")
        def admin_dashboard():
            ...

    Behavior:
      - Not logged in at all           -> sent to the role-selection page.
      - Logged in but WRONG role       -> sent to their OWN dashboard
                                           (not a blank 403 - a role's
                                           account should never see a
                                           different role's protected page).
      - Logged in with the RIGHT role  -> request proceeds normally.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for("auth.role_select"))

            if current_user.role != required_role:
                fallback = _OWN_DASHBOARD.get(current_user.role, "auth.role_select")
                return redirect(url_for(fallback))

            return view_func(*args, **kwargs)
        return wrapped_view
    return decorator
