import os

PUBLIC_API_URL = os.getenv("PUBLIC_API_URL", "http://localhost:8000")


def get_enrollment_completed_email_html(
    name: str,
    course: str,
    start_date: str,
) -> str:
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
                <table role="presentation" width="520" cellpadding="0" cellspacing="0" style="background-color:#ffffff; border-radius:12px; overflow:hidden; box-shadow:0 4px 16px rgba(0,0,0,0.08);">
                    <!-- Header -->
                    <tr>
                        <td style="background:#ffffff; padding:30px 40px 20px; text-align:center; border-bottom:3px solid #166534;">
                            <img src="{logo_url}" alt="Bright Horizon Institute" style="height:70px; display:inline-block;" />
                        </td>
                    </tr>

                    <!-- Green Banner -->
                    <tr>
                        <td style="background:linear-gradient(135deg, #14532d 0%, #166534 100%); padding:28px 40px; text-align:center;">
                            <p style="margin:0 0 6px; color:rgba(255,255,255,0.8); font-size:13px; text-transform:uppercase; letter-spacing:0.1em;">Congratulations</p>
                            <h1 style="margin:0; color:#ffffff; font-size:24px; font-weight:700;">Enrollment Complete!</h1>
                        </td>
                    </tr>

                    <!-- Body -->
                    <tr>
                        <td style="padding:36px 40px 20px;">
                            <p style="margin:0 0 20px; color:#334155; font-size:15px; line-height:1.7;">
                                Dear <strong>{name}</strong>,
                            </p>
                            <p style="margin:0 0 20px; color:#334155; font-size:15px; line-height:1.7;">
                                We are pleased to confirm that your enrollment for <strong>{course}</strong> has been <strong>successfully completed</strong>. You are now officially a student at Bright Horizon Institute.
                            </p>

                            <!-- Success Box -->
                            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 25px;">
                                <tr>
                                    <td align="center" style="background:#f0fdf4; border:1px solid #bbf7d0; border-radius:10px; padding:24px;">
                                        <div style="font-size:40px; margin-bottom:8px;">&#127891;</div>
                                        <p style="margin:0; font-size:17px; color:#166534; font-weight:700;">Welcome, Student!</p>
                                        <p style="margin:6px 0 0; font-size:14px; color:#15803d;">Your student account has been activated.</p>
                                    </td>
                                </tr>
                            </table>

                            <!-- Course Info -->
                            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 25px; border:1px solid #e2e8f0; border-radius:10px; overflow:hidden;">
                                <tr>
                                    <td colspan="2" style="background:#f8fafc; padding:14px 20px; border-bottom:1px solid #eef2f7;">
                                        <strong style="color:#1a1a2e; font-size:14px; text-transform:uppercase; letter-spacing:0.05em;">Your Course</strong>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding:12px 20px; border-bottom:1px solid #eef2f7;">
                                        <span style="color:#64748b; font-size:13px; text-transform:uppercase; letter-spacing:0.05em;">Course</span><br>
                                        <strong style="color:#1a1a2e; font-size:16px;">{course}</strong>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding:12px 20px;">
                                        <span style="color:#64748b; font-size:13px; text-transform:uppercase; letter-spacing:0.05em;">Class Start Date</span><br>
                                        <strong style="color:#166534; font-size:16px;">{start_date}</strong>
                                    </td>
                                </tr>
                            </table>

                            <!-- What's Next -->
                            <h3 style="margin:0 0 14px; color:#1a1a2e; font-size:16px;">What happens next?</h3>
                            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 25px;">
                                <tr>
                                    <td style="padding:6px 0; color:#334155; font-size:14px; line-height:1.6;">
                                        &#10003; You now have a <strong>student account</strong> at Bright Horizon Institute.
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding:6px 0; color:#334155; font-size:14px; line-height:1.6;">
                                        &#10003; Please be ready to attend class on the scheduled <strong>start date</strong>.
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding:6px 0; color:#334155; font-size:14px; line-height:1.6;">
                                        &#10003; Our team will share additional details about your class schedule and orientation.
                                    </td>
                                </tr>
                            </table>

                            <p style="margin:0 0 8px; color:#334155; font-size:15px; line-height:1.7;">
                                We are excited to have you on board and look forward to a great learning experience. If you have any questions, please don't hesitate to reach out.
                            </p>
                        </td>
                    </tr>

                    <!-- Contact -->
                    <tr>
                        <td style="padding:0 40px 30px; text-align:center;">
                            <p style="margin:0; color:#64748b; font-size:13px; line-height:1.6;">
                                Questions? Contact us at<br>
                                <a href="mailto:support@brighthii.com" style="color:#166534; text-decoration:none; font-weight:600;">support@brighthii.com</a>
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
