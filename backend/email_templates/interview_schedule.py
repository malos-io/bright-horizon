import os

PUBLIC_API_URL = os.getenv("PUBLIC_API_URL", "http://localhost:8000")


def get_interview_schedule_email_html(
    name: str,
    course: str,
    start_date: str,
    enrollment_deadline: str | None,
) -> str:
    logo_url = f"{PUBLIC_API_URL}/static/logo-email.png"

    deadline_row = ""
    if enrollment_deadline:
        deadline_row = f"""
                                <tr>
                                    <td style="padding:12px 20px; border-bottom:1px solid #eef2f7;">
                                        <span style="color:#64748b; font-size:13px; text-transform:uppercase; letter-spacing:0.05em;">Enrollment Deadline</span><br>
                                        <strong style="color:#dc2626; font-size:16px;">{enrollment_deadline}</strong>
                                    </td>
                                </tr>"""

    deadline_note = ""
    if enrollment_deadline:
        deadline_note = f"""
                            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 25px;">
                                <tr>
                                    <td style="background:#fef2f2; border:1px solid #fecaca; border-radius:8px; padding:14px 18px;">
                                        <p style="margin:0; color:#991b1b; font-size:14px; line-height:1.5;">
                                            <strong>Important:</strong> Please complete your enrollment on or before <strong>{enrollment_deadline}</strong>. Failure to enroll by this date may result in forfeiture of your slot.
                                        </p>
                                    </td>
                                </tr>
                            </table>"""

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
                        <td style="background:#ffffff; padding:30px 40px 20px; text-align:center; border-bottom:3px solid #1a5fa4;">
                            <img src="{logo_url}" alt="Bright Horizon Institute" style="height:70px; display:inline-block;" />
                        </td>
                    </tr>

                    <!-- Blue Banner -->
                    <tr>
                        <td style="background:linear-gradient(135deg, #0d3b6e 0%, #1a5fa4 100%); padding:28px 40px; text-align:center;">
                            <p style="margin:0 0 6px; color:rgba(255,255,255,0.8); font-size:13px; text-transform:uppercase; letter-spacing:0.1em;">Next Step in Your Enrollment</p>
                            <h1 style="margin:0; color:#ffffff; font-size:24px; font-weight:700;">Physical Documents &amp; Interview</h1>
                        </td>
                    </tr>

                    <!-- Body -->
                    <tr>
                        <td style="padding:36px 40px 20px;">
                            <p style="margin:0 0 20px; color:#334155; font-size:15px; line-height:1.7;">
                                Dear <strong>{name}</strong>,
                            </p>
                            <p style="margin:0 0 20px; color:#334155; font-size:15px; line-height:1.7;">
                                Congratulations! Your application documents for <strong>{course}</strong> have been reviewed and accepted. You are now required to <strong>visit our training center in person</strong> to complete the next steps of your enrollment.
                            </p>

                            <!-- Action Required Box -->
                            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 25px;">
                                <tr>
                                    <td style="background:#eff6ff; border:1px solid #bfdbfe; border-radius:10px; padding:20px 24px;">
                                        <h3 style="margin:0 0 10px; color:#1e40af; font-size:15px;">What you need to do:</h3>
                                        <p style="margin:0; color:#1e40af; font-size:14px; line-height:1.7;">
                                            Report to <strong>Bright Horizon Institute</strong> to submit the <strong>original copies</strong> of your documents for physical verification and undergo a brief interview with our admissions team.
                                        </p>
                                    </td>
                                </tr>
                            </table>

                            <!-- Course Schedule Info -->
                            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 25px; border:1px solid #e2e8f0; border-radius:10px; overflow:hidden;">
                                <tr>
                                    <td colspan="2" style="background:#f8fafc; padding:14px 20px; border-bottom:1px solid #eef2f7;">
                                        <strong style="color:#1a1a2e; font-size:14px; text-transform:uppercase; letter-spacing:0.05em;">Course Information</strong>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding:12px 20px; border-bottom:1px solid #eef2f7;">
                                        <span style="color:#64748b; font-size:13px; text-transform:uppercase; letter-spacing:0.05em;">Course</span><br>
                                        <strong style="color:#1a1a2e; font-size:16px;">{course}</strong>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding:12px 20px; border-bottom:1px solid #eef2f7;">
                                        <span style="color:#64748b; font-size:13px; text-transform:uppercase; letter-spacing:0.05em;">Class Start Date</span><br>
                                        <strong style="color:#166534; font-size:16px;">{start_date}</strong>
                                    </td>
                                </tr>{deadline_row}
                            </table>

                            {deadline_note}

                            <!-- Documents Checklist -->
                            <h3 style="margin:0 0 14px; color:#1a1a2e; font-size:16px;">Please bring the following:</h3>
                            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 25px;">
                                <tr>
                                    <td style="padding:6px 0; color:#334155; font-size:14px; line-height:1.6;">
                                        &#9745; Original <strong>Birth Certificate</strong> (PSA/NSO)
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding:6px 0; color:#334155; font-size:14px; line-height:1.6;">
                                        &#9745; Original <strong>Educational Credentials</strong> (TOR / Diploma / Form 137)
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding:6px 0; color:#334155; font-size:14px; line-height:1.6;">
                                        &#9745; Valid <strong>Government-Issued ID</strong>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding:6px 0; color:#334155; font-size:14px; line-height:1.6;">
                                        &#9745; <strong>1x1</strong> and <strong>2x2 ID Photos</strong> (1 copy each, white background) &mdash; or have them taken at our office
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding:6px 0; color:#334155; font-size:14px; line-height:1.6;">
                                        &#9745; <strong>Proof of Name Change</strong> (if applicable &mdash; marriage certificate, court order, etc.)
                                    </td>
                                </tr>
                            </table>

                            <!-- Note -->
                            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 25px;">
                                <tr>
                                    <td style="background:#fffbeb; border:1px solid #fde68a; border-radius:8px; padding:14px 18px;">
                                        <p style="margin:0; color:#92400e; font-size:13px; line-height:1.6;">
                                            <strong>Note:</strong> The interview is a brief, informal conversation with our admissions officer. It is not an examination. Please arrive during office hours (Monday&ndash;Friday, 8:00 AM&ndash;5:00 PM).
                                        </p>
                                    </td>
                                </tr>
                            </table>

                            <p style="margin:0 0 8px; color:#334155; font-size:15px; line-height:1.7;">
                                We look forward to seeing you at Bright Horizon Institute. If you have any questions or need assistance, please don't hesitate to reach out.
                            </p>
                        </td>
                    </tr>

                    <!-- Contact -->
                    <tr>
                        <td style="padding:0 40px 30px; text-align:center;">
                            <p style="margin:0; color:#64748b; font-size:13px; line-height:1.6;">
                                Questions? Contact us at<br>
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
