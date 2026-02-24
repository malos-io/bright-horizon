import os

PUBLIC_API_URL = os.getenv("PUBLIC_API_URL", "http://localhost:8000")


def get_batch_removed_email_html(name: str, course: str) -> str:
    logo_url = f"{PUBLIC_API_URL}/static/logo-email.png"

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
                            <h2 style="margin:0 0 10px; color:#1a1a2e; font-size:22px;">Class Schedule Update</h2>
                            <p style="margin:0 0 20px; color:#555; font-size:15px; line-height:1.6;">
                                Hi {name},
                            </p>
                            <p style="margin:0 0 20px; color:#555; font-size:15px; line-height:1.6;">
                                Your class schedule for <strong>{course}</strong> has been updated. We will notify you once a new class date is available.
                            </p>
                            <!-- Info Box -->
                            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 25px;">
                                <tr>
                                    <td align="center" style="background:#eff6ff; border:1px solid #bfdbfe; border-radius:10px; padding:24px;">
                                        <p style="margin:0; font-size:15px; color:#1e40af; line-height:1.6;">
                                            Your enrollment for <strong>{course}</strong> is still active.<br>
                                            We will be in touch with your updated class schedule soon.
                                        </p>
                                    </td>
                                </tr>
                            </table>
                            <p style="margin:0; color:#888; font-size:13px; line-height:1.6; text-align:center;">
                                If you have any questions, please contact us at<br>
                                <a href="mailto:support@brighthii.com" style="color:#1a5fa4; text-decoration:none; font-weight:600;">support@brighthii.com</a>
                            </p>
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
