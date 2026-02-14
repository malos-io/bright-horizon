import os

PUBLIC_API_URL = os.getenv("PUBLIC_API_URL", "http://localhost:8000")
ADMIN_FRONTEND_URL = os.getenv("ADMIN_FRONTEND_URL", "http://localhost:5174")


def get_admin_application_withdrawn_email_html(
    applicant_name: str,
    email: str,
    course: str,
    enrollment_id: str,
    reason: str,
    comments: str = "",
) -> str:
    logo_url = f"{PUBLIC_API_URL}/static/logo-email.png"
    review_url = f"{ADMIN_FRONTEND_URL}/enrollments/{enrollment_id}"

    comments_row = ""
    if comments:
        comments_row = f"""<tr>
                                                <td style="padding:6px 0; color:#888; font-size:13px; vertical-align:top;">Comments</td>
                                                <td style="padding:6px 0; color:#1a1a2e; font-size:15px;">{comments}</td>
                                            </tr>"""

    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0; padding:0; background-color:#f4f6f9; font-family:Arial, Helvetica, sans-serif;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#f4f6f9; padding:40px 0;">
        <tr>
            <td align="center">
                <table role="presentation" width="480" cellpadding="0" cellspacing="0" style="background-color:#ffffff; border-radius:12px; overflow:hidden; box-shadow:0 2px 8px rgba(0,0,0,0.08);">
                    <!-- Header -->
                    <tr>
                        <td style="background:#ffffff; padding:30px 40px; text-align:center; border-bottom:2px solid #e8e8e8;">
                            <img src="{logo_url}" alt="Bright Horizon Institute" style="height:70px; display:inline-block;" />
                        </td>
                    </tr>
                    <!-- Body -->
                    <tr>
                        <td style="padding:40px;">
                            <h2 style="margin:0 0 10px; color:#1a1a2e; font-size:22px;">Application Withdrawn</h2>
                            <p style="margin:0 0 20px; color:#555; font-size:15px; line-height:1.6;">
                                An applicant has withdrawn their enrollment application. Here are the details:
                            </p>
                            <!-- Applicant Details -->
                            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 25px;">
                                <tr>
                                    <td style="background:#fef2f2; border:1px solid #fecaca; border-radius:10px; padding:20px 24px;">
                                        <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
                                            <tr>
                                                <td style="padding:6px 0; color:#888; font-size:13px; width:100px;">Name</td>
                                                <td style="padding:6px 0; color:#1a1a2e; font-size:15px; font-weight:600;">{applicant_name}</td>
                                            </tr>
                                            <tr>
                                                <td style="padding:6px 0; color:#888; font-size:13px;">Email</td>
                                                <td style="padding:6px 0; color:#1a1a2e; font-size:15px;">{email}</td>
                                            </tr>
                                            <tr>
                                                <td style="padding:6px 0; color:#888; font-size:13px;">Course</td>
                                                <td style="padding:6px 0; color:#991b1b; font-size:15px; font-weight:700;">{course}</td>
                                            </tr>
                                            <tr>
                                                <td style="padding:6px 0; color:#888; font-size:13px;">Reason</td>
                                                <td style="padding:6px 0; color:#1a1a2e; font-size:15px; font-weight:600;">{reason}</td>
                                            </tr>
                                            {comments_row}
                                        </table>
                                    </td>
                                </tr>
                            </table>
                            <!-- CTA Button -->
                            <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
                                <tr>
                                    <td align="center" style="padding:0 0 25px;">
                                        <a href="{review_url}" style="display:inline-block; background:#1a5fa4; color:#ffffff; font-size:15px; font-weight:600; padding:14px 32px; border-radius:8px; text-decoration:none;">View Application</a>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    <!-- Footer -->
                    <tr>
                        <td style="background:#f8f9fb; padding:20px 40px; border-top:1px solid #eee; text-align:center;">
                            <p style="margin:0; color:#aaa; font-size:12px;">
                                &copy; 2026 Bright Horizon Institute Inc.<br>
                                This is an automated message. Please do not reply.
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>"""
