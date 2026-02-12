import os

PUBLIC_API_URL = os.getenv("PUBLIC_API_URL", "http://localhost:8000")
PUBLIC_FRONTEND_URL = os.getenv("PUBLIC_FRONTEND_URL", "http://localhost:5173")


def get_document_rejected_email_html(name: str, document_label: str, reject_reason: str) -> str:
    logo_url = f"{PUBLIC_API_URL}/static/logo-email.png"
    track_url = f"{PUBLIC_FRONTEND_URL}/track-application"

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
                            <h2 style="margin:0 0 10px; color:#1a1a2e; font-size:22px;">Document Requires Re-upload</h2>
                            <p style="margin:0 0 20px; color:#555; font-size:15px; line-height:1.6;">
                                Hi {name},
                            </p>
                            <p style="margin:0 0 20px; color:#555; font-size:15px; line-height:1.6;">
                                We have reviewed your submitted document and unfortunately it could not be accepted at this time. Please see the details below:
                            </p>
                            <!-- Document Details Box -->
                            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 20px;">
                                <tr>
                                    <td style="background:#fef2f2; border:1px solid #fecaca; border-radius:10px; padding:20px;">
                                        <p style="margin:0 0 8px; font-size:13px; color:#991b1b; font-weight:600; text-transform:uppercase; letter-spacing:0.5px;">Document</p>
                                        <p style="margin:0 0 16px; font-size:16px; color:#1a1a2e; font-weight:700;">{document_label}</p>
                                        <p style="margin:0 0 8px; font-size:13px; color:#991b1b; font-weight:600; text-transform:uppercase; letter-spacing:0.5px;">Reason</p>
                                        <p style="margin:0; font-size:15px; color:#333; line-height:1.5;">{reject_reason}</p>
                                    </td>
                                </tr>
                            </table>
                            <h3 style="margin:0 0 12px; color:#1a1a2e; font-size:16px;">What to do next:</h3>
                            <ol style="margin:0 0 25px; padding-left:20px; color:#555; font-size:14px; line-height:1.8;">
                                <li>Visit the <a href="{track_url}" style="color:#1a5fa4; text-decoration:none; font-weight:600;">Track Application</a> page</li>
                                <li>Verify your email to access your application</li>
                                <li>Click <strong>"See Application"</strong> to view your documents</li>
                                <li>Re-upload a corrected version of your <strong>{document_label}</strong></li>
                            </ol>
                            <!-- CTA Button -->
                            <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
                                <tr>
                                    <td align="center" style="padding:5px 0 20px;">
                                        <a href="{track_url}" style="display:inline-block; background:#1a5fa4; color:#ffffff; font-size:15px; font-weight:600; padding:14px 32px; border-radius:8px; text-decoration:none;">Re-upload Document</a>
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
