import re
import smtplib
import urllib.request

from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.message import EmailMessage

import coreapi.compat
from rest_framework.response import Response
from rest_framework import status
from email.mime.image import MIMEImage


def send_gmail(mail_info, attachment):
    
    gmail_user = mail_info['gmail_user']
    gmail_password = mail_info['gmail_password']
    sent_from = mail_info['sent_from']
    send_to = mail_info['send_to']

    # sent_from = 'greenbi5693@naver.com'
    # send_to = 'greenbi5693@naver.com'
    
    
    if attachment is None:
        msg = MIMEText(mail_info['body'])
        msg['Subject'] = mail_info['subject']
        
    else:
        # Create a multipart message and set headers
        msg = EmailMessage()
        msg['From'] = sent_from
        msg['To'] = send_to
        msg['Subject'] = mail_info['subject']
        # message["Bcc"] = receiver_email  # Recommended for mass emails   
        
        # Add body to email
        body = MIMEText(mail_info['body'], "utf-8")
        msg.attach(body)
        
        filename = attachment
        # Open PDF file in binary mode
        with open(filename, "rb") as attachment:
            # Add file as application/octet-stream
            # Email client can usually download this automatically as attachment
            part =  MIMEBase("application", 'octet-stream')
            part.set_payload(attachment.read())

        # Encode file in ASCII characters to send by email    
        encoders.encode_base64(part)

        # Add header as key/value pair to attachment part
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {filename}",
        )
        msg.attach(part)

    try:
        # server = smtplib.SMTP('smtp.googlemail.com', 587)
        server = smtplib.SMTP('smtp.gmail.com', 587)

        server.starttls()
        server.login(gmail_user, gmail_password)
        server.sendmail(sent_from, send_to, msg.as_string())
        server.close()
        print("Send email......!!!")

    except Exception as ex:
        print('Something went wrong...')
        print(ex)


def send_gmail_pdf(mail_info, attachment):
    gmail_user = mail_info['gmail_user']
    gmail_password = mail_info['gmail_password']
    sent_from = mail_info['sent_from']
    send_to = mail_info['send_to']
    # send_cc = mail_info['Cc']
    send_bcc = mail_info['Bcc']
    send_type = mail_info['type']
    sent_enterprise = mail_info['enterprise']
    enter_email = mail_info['enter_email']
    enter_fax = mail_info['enter_fax']
    enter_call = mail_info['enter_call']
    logo_img = mail_info['logo_img']

    if attachment is None:
        msg = MIMEText(send_type)
        msg['Subject'] = mail_info['subject']

    else:
        # Create a multipart message and set headers
        # 메일을 보냈을 때 '보내는 사람, 받는 사람, 참조, 숨은 참조 표시
        msg = EmailMessage()
        msg['From'] = sent_from
        msg['To'] = send_to
        # msg['Cc'] = send_cc
        msg['Subject'] = mail_info['subject']

        # domain_re = re.compile('@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
        # domain = domain_re.search(send_to).group()

        if logo_img:
            html = f"""
                        <html>
                        <head>
                        </head>
                            <body>
                                <table border="1" cellpadding="10px" cellspacing="0px" width="100%">
                                    <tr>
                                        <td align='left' bgcolor='#46516B'>
                                            <br>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td bgcolor="#ffffff" style='color:#000000; ' width='100%' height='100%'>
                                            <p>{sent_enterprise} ({send_type}) 입니다.<br>첨부 파일 확인 바랍니다.<br><br></p>
                                            <p>본 메일은 발신전용입니다.<br>문의 및 회신은 하단을 참조하여 주시기 바랍니다.<br><br></p>
                                            <p style="font-weight: bold; font-size: 11pt;">
                                                {sent_enterprise} 전화번호 : <a style="color:#F79444;">{enter_call}</a><br>
                                                {sent_enterprise} FAX : <a style="color:#F79444;">{enter_fax}</a><br>
                                                {sent_enterprise} Email : <a style="color:#F79444;">{enter_email}</a>
                                            </p>
                                            <img src='{logo_img}' align='right' alt='logo' style='display:block'/>
                                        </td>
                                    </tr>
                                </table>
                            </body>
                        </html>
                    """

        else:
            html = f"""
                                    <html>
                                    <head>
                                    </head>
                                        <body>
                                            <table border="1" cellpadding="10px" cellspacing="0px" width="100%">
                                                <tr>
                                                    <td align='left' bgcolor='#46516B'>
                                                        <br>
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <td bgcolor="#ffffff" style='color:#000000; ' width='100%' height='100%'>
                                                        <p>{sent_enterprise} ({send_type}) 입니다.<br>첨부 파일 확인 바랍니다.<br><br></p>
                                                        <p>본 메일은 발신전용입니다.<br>문의 및 회신은 하단을 참조하여 주시기 바랍니다.<br><br></p>
                                                        <p style="font-weight: bold; font-size: 11pt;">
                                                            {sent_enterprise} 전화번호 : <a style="color:#F79444;">{enter_call}</a><br>
                                                            {sent_enterprise} FAX : <a style="color:#F79444;">{enter_fax}</a><br>
                                                            {sent_enterprise} Email : <a style="color:#F79444;">{enter_email}</a>
                                                        </p>
                                                    </td>
                                                </tr>
                                            </table>
                                        </body>
                                    </html>
                                """

        # Add body to email
        msg.add_alternative(html, "html")

        #with open("C:/Users/YuBin/Desktop/test_image.jfif", "rb") as img:
        with open("C:/Users/newjin/Desktop/test_img.jpg", "rb") as img:
            test_img = MIMEImage(img.read(), 'jpeg')
            test_img.add_header('Content-ID', '<image1>')
            msg.attach(test_img)

        filename = send_type + ".pdf"
        part = MIMEBase("application", 'octet-stream')
        part.set_payload(attachment.read())

        # Encode file in ASCII characters to send by email
        encoders.encode_base64(part)

        # Add header as key/value pair to attachment part
        part.add_header(
            "Content-Disposition",
            "attachment", filename=filename,
        )
        msg.attach(part)

    try:
        # server = smtplib.SMTP('smtp.googlemail.com', 587)
        server = smtplib.SMTP('smtp.gmail.com', 587)

        server.starttls()
        server.login(gmail_user, gmail_password)

        # 메일을 보냈을 때 '보내는 사람, 받는 사람, 참조, 숨은 참조' 실제로 전달 되는 곳
        server.sendmail(sent_from, send_to.split(',') + send_bcc.split(','), msg.as_string())
        server.close()
        print("Send email......!!!")

    except Exception as ex:
        print('Something went wrong...')
        print(ex)


        
if __name__ == '__main__':

    subject = '제목 : 메일 보내기 테스트입니다.'
    body = '내용 : 본문내용 테스트입니다.'
    
    mail_info = dict(gmail_user='ssmesdev@gmail.com',
                     gmail_password='mes_developer1',
                     send_to=['grammaright@me.com'],
                     subject=subject, body=body
                    )
    
    attachment = None  # filename if exists else; None
    
    send_gmail(mail_info, attachment)
