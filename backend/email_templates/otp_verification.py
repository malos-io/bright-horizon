import os

PUBLIC_API_URL = os.getenv("PUBLIC_API_URL", "http://localhost:8000")


def get_otp_email_html(code: str, name: str) -> str:
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
                            <h2 style="margin:0 0 10px; color:#1a1a2e; font-size:22px;">Verification Code</h2>
                            <p style="margin:0 0 25px; color:#555; font-size:15px; line-height:1.5;">
                                Hi {name},<br>
                                Use the code below to verify your identity and track your application status.
                            </p>
                            <!-- OTP Code Box -->
                            <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
                                <tr>
                                    <td align="center" style="padding:20px 0;">
                                        <div style="display:inline-block; background:#f0f4ff; border:2px dashed #1a5fa4; border-radius:10px; padding:18px 40px; letter-spacing:12px; font-size:36px; font-weight:700; color:#0d3b6e;">
                                            {code}
                                        </div>
                                    </td>
                                </tr>
                            </table>
                            <p style="margin:25px 0 0; color:#888; font-size:13px; text-align:center;">
                                This code expires in <strong>10 minutes</strong>.<br>
                                If you did not request this, please ignore this email.
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
