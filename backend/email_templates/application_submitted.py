import os

PUBLIC_API_URL = os.getenv("PUBLIC_API_URL", "http://localhost:8000")
PUBLIC_FRONTEND_URL = os.getenv("PUBLIC_FRONTEND_URL", "http://localhost:5173")


def get_application_submitted_email_html(name: str, course: str) -> str:
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
                            <h2 style="margin:0 0 10px; color:#1a1a2e; font-size:22px;">Application Received!</h2>
                            <p style="margin:0 0 20px; color:#555; font-size:15px; line-height:1.6;">
                                Hi {name},
                            </p>
                            <p style="margin:0 0 20px; color:#555; font-size:15px; line-height:1.6;">
                                Thank you for your interest in enrolling at Bright Horizon Institute. We have received your application for:
                            </p>
                            <!-- Course Box -->
                            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 25px;">
                                <tr>
                                    <td align="center" style="background:#f0f4ff; border:1px solid #c7d8f4; border-radius:10px; padding:18px 24px;">
                                        <p style="margin:0; font-size:17px; color:#0d3b6e; font-weight:700;">{course}</p>
                                    </td>
                                </tr>
                            </table>
                            <h3 style="margin:0 0 14px; color:#1a1a2e; font-size:16px;">What happens next?</h3>
                            <p style="margin:0 0 16px; color:#555; font-size:14px; line-height:1.5;">
                                Here is an overview of the enrollment process:
                            </p>
                            <!-- Steps -->
                            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 25px;">
                                <tr>
                                    <td style="padding:12px 16px; background:#f8f9fb; border-radius:8px 8px 0 0; border-bottom:1px solid #eee;">
                                        <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
                                            <tr>
                                                <td width="32" valign="top" style="color:#1a5fa4; font-weight:700; font-size:15px;">1.</td>
                                                <td style="color:#333; font-size:14px; line-height:1.5;"><strong>Upload Required Documents</strong><br><span style="color:#666;">Submit your Birth Certificate, Educational Credentials, and Government ID through the Track Application page.</span></td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding:12px 16px; background:#f8f9fb; border-bottom:1px solid #eee;">
                                        <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
                                            <tr>
                                                <td width="32" valign="top" style="color:#1a5fa4; font-weight:700; font-size:15px;">2.</td>
                                                <td style="color:#333; font-size:14px; line-height:1.5;"><strong>Document Review</strong><br><span style="color:#666;">Our admissions team will review your submitted documents. You will be notified if any document needs to be re-uploaded.</span></td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding:12px 16px; background:#f8f9fb; border-bottom:1px solid #eee;">
                                        <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
                                            <tr>
                                                <td width="32" valign="top" style="color:#1a5fa4; font-weight:700; font-size:15px;">3.</td>
                                                <td style="color:#333; font-size:14px; line-height:1.5;"><strong>Waitlist Placement</strong><br><span style="color:#666;">Once all documents are accepted, you will be placed on the waitlist for your selected course.</span></td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding:12px 16px; background:#f8f9fb; border-bottom:1px solid #eee;">
                                        <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
                                            <tr>
                                                <td width="32" valign="top" style="color:#1a5fa4; font-weight:700; font-size:15px;">4.</td>
                                                <td style="color:#333; font-size:14px; line-height:1.5;"><strong>Class Schedule Notification</strong><br><span style="color:#666;">You will be notified once a final start date has been set for your selected class.</span></td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding:12px 16px; background:#f8f9fb; border-bottom:1px solid #eee;">
                                        <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
                                            <tr>
                                                <td width="32" valign="top" style="color:#1a5fa4; font-weight:700; font-size:15px;">5.</td>
                                                <td style="color:#333; font-size:14px; line-height:1.5;"><strong>Interview &amp; Verification</strong><br><span style="color:#666;">You will be invited for a final interview and on-site verification process.</span></td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding:12px 16px; background:#f8f9fb; border-radius:0 0 8px 8px;">
                                        <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
                                            <tr>
                                                <td width="32" valign="top" style="color:#1a5fa4; font-weight:700; font-size:15px;">6.</td>
                                                <td style="color:#333; font-size:14px; line-height:1.5;"><strong>Enrollment Confirmed</strong><br><span style="color:#666;">After successful verification, you will be officially enrolled as a student.</span></td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>
                            <!-- CTA Button -->
                            <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
                                <tr>
                                    <td align="center" style="padding:0 0 25px;">
                                        <a href="{track_url}" style="display:inline-block; background:#1a5fa4; color:#ffffff; font-size:15px; font-weight:600; padding:14px 32px; border-radius:8px; text-decoration:none;">Track Your Application</a>
                                    </td>
                                </tr>
                            </table>
                            <p style="margin:0; color:#888; font-size:13px; line-height:1.6; text-align:center;">
                                If you have any questions, please email us at<br>
                                <a href="mailto:support@brighthii.com" style="color:#1a5fa4; text-decoration:none; font-weight:600;">support@brighthii.com</a><br>
                                or visit our <strong>Contact Us</strong> page for our phone number.
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
