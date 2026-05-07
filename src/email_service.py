import os
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class EmailService:
    """Email service for alerts and notifications"""

    def __init__(self):
        self.enabled = bool(os.getenv('SMTP_ENABLED', False))
        self.from_email = os.getenv('SMTP_FROM_EMAIL', 'alerts@luxurytravelagent.com')
        self.smtp_host = os.getenv('SMTP_HOST')
        self.smtp_port = os.getenv('SMTP_PORT', 587)
        self.smtp_user = os.getenv('SMTP_USER')
        self.smtp_password = os.getenv('SMTP_PASSWORD')

        if self.enabled:
            try:
                import smtplib
                self.smtplib = smtplib
                logger.info("Email service configured and enabled")
            except ImportError:
                logger.warning("smtplib not available")
                self.enabled = False
        else:
            logger.info("Email service disabled (demo mode)")

    def send_price_alert(self, user_email: str, route: Dict, deal: Dict) -> bool:
        """Send price drop alert email"""
        subject = f"Price Drop Alert: {route['origin']} → {route['destination']}"
        body = self._build_price_alert_email(route, deal)
        return self.send_email(user_email, subject, body)

    def send_award_alert(self, user_email: str, route: Dict, award: Dict) -> bool:
        """Send award availability alert"""
        subject = f"Award Available: {route['origin']} → {route['destination']}"
        body = self._build_award_alert_email(route, award)
        return self.send_email(user_email, subject, body)

    def send_welcome_email(self, user_email: str, first_name: str) -> bool:
        """Send welcome email to new user"""
        subject = "Welcome to Luxury Travel Agent"
        body = self._build_welcome_email(first_name)
        return self.send_email(user_email, subject, body)

    def send_email_verification(self, user_email: str, verification_link: str) -> bool:
        """Send email verification link"""
        subject = "Verify Your Email - Luxury Travel Agent"
        body = self._build_verification_email(verification_link)
        return self.send_email(user_email, subject, body)

    def send_email(self, to_email: str, subject: str, body: str) -> bool:
        """Send email via SMTP"""
        if not self.enabled:
            logger.warning(f"Email not sent (disabled): {to_email} - {subject}")
            return False

        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart

            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email

            # HTML version
            html_body = f"""
            <html>
              <body>
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                  {body}
                  <hr style="border: none; border-top: 1px solid #ccc; margin: 20px 0;">
                  <p style="color: #666; font-size: 12px;">
                    Luxury Travel Agent<br>
                    <a href="https://luxurytravelagent.com">Visit Platform</a>
                  </p>
                </div>
              </body>
            </html>
            """

            msg.attach(MIMEText(body, 'plain'))
            msg.attach(MIMEText(html_body, 'html'))

            with smtplib.SMTP(self.smtp_host, int(self.smtp_port)) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Email sent to {to_email}: {subject}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False

    @staticmethod
    def _build_price_alert_email(route: Dict, deal: Dict) -> str:
        return f"""
        <h2>✈️ Price Drop Alert!</h2>
        <p>Great news! The price for your route has dropped.</p>

        <div style="background: #f5f5f5; padding: 15px; border-radius: 5px;">
            <p><strong>{route['origin']} → {route['destination']}</strong></p>
            <p><strong>Price:</strong> ${deal['price']:.2f}</p>
            <p><strong>Cabin:</strong> {deal.get('cabin', 'Economy')}</p>
            <p><strong>CPP:</strong> {deal.get('cpp', 'N/A')}</p>
        </div>

        <p><a href="https://luxurytravelagent.com/search?origin={route['origin']}&destination={route['destination']}"
              style="background: #d4af37; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
              View Deal
        </a></p>
        """

    @staticmethod
    def _build_award_alert_email(route: Dict, award: Dict) -> str:
        return f"""
        <h2>🏆 Award Available!</h2>
        <p>Award availability for your route just became available.</p>

        <div style="background: #f5f5f5; padding: 15px; border-radius: 5px;">
            <p><strong>{route['origin']} → {route['destination']}</strong></p>
            <p><strong>Program:</strong> {award.get('program', 'Unknown')}</p>
            <p><strong>Miles Required:</strong> {award.get('miles', 'N/A'):,}</p>
            <p><strong>Cabin:</strong> {award.get('cabin', 'Economy')}</p>
            <p><strong>Taxes/Fees:</strong> ${award.get('taxes', 0):.2f}</p>
        </div>

        <p><a href="https://luxurytravelagent.com/search?origin={route['origin']}&destination={route['destination']}&tab=awards"
              style="background: #d4af37; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
              View Award
        </a></p>
        """

    @staticmethod
    def _build_welcome_email(first_name: str) -> str:
        return f"""
        <h2>Welcome to Luxury Travel Agent! 🌍</h2>
        <p>Hi {first_name},</p>
        <p>Thanks for joining Luxury Travel Agent! We help you find the best travel deals by comparing:</p>

        <ul>
            <li>💰 Flight prices across airlines</li>
            <li>🏆 Award availability and value</li>
            <li>📊 Deal insights and trends</li>
            <li>⚡ Price alerts and notifications</li>
        </ul>

        <p><strong>Get started:</strong></p>
        <ol>
            <li>Search for your next trip</li>
            <li>Set up price alerts</li>
            <li>Link your loyalty accounts</li>
            <li>Save your favorite deals</li>
        </ol>

        <p>Happy travels!</p>
        """

    @staticmethod
    def _build_verification_email(verification_link: str) -> str:
        return f"""
        <h2>Verify Your Email</h2>
        <p>Click the button below to verify your email address:</p>

        <p><a href="{verification_link}"
              style="background: #d4af37; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">
              Verify Email
        </a></p>

        <p style="color: #666; font-size: 12px;">
            Or copy this link: <code>{verification_link}</code>
        </p>

        <p style="color: #666; font-size: 12px;">
            This link expires in 24 hours.
        </p>
        """


# Global instance
email_service = EmailService()
