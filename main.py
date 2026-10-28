import tkinter as tk  # מייבא את ספריית tkinter ליצירת תצוגה גרפית, חלונות וכפתורים בפייתון
from tcp_client import send_request  # תקשורת TCP באמצעות Windows Winsock

# הגדרת כתובת האינטרנט (URL) של שרת ה-Flask שאליו הלקוח ישלח את נתוני ההתחברות וההרשמה

# --- הגדרת החלון הראשי ---
root = tk.Tk()  # יוצר את אובייקט החלון הראשי של התוכנית ושומר אותו במשתנה root
root.title("מערכת אבטחה - הזדהות")  # מגדיר את הטקסט שיופיע בכותרת החלון העליונה
root.geometry("700x750")  # קובע את רוחב החלון ל-700 פיקסלים ואת גובה החלון ל-750 פיקסלים
root.resizable(False, False)  # מונע מהמשתמש לשנות את גודל החלון בעזרת העכבר
root.configure(bg="#0a61c7")  # צובע את רקע החלון הראשי בצבע כחול (קוד צבע #0a61c7)

# משטח ציור (Canvas) עבור הממשק
canvas = tk.Canvas(root, bg="#0a61c7", highlightthickness=0)  # יוצר משטח ציור גמיש בעל רקע כחול ללא מסגרת
canvas.place(x=0, y=0, width=700, height=750)  # ממקם את משטח הציור בפינה העליונה ומותח אותו על כל החלון

# פונקציה לציור מלבן מעוגל מותאם אישית
def draw_rounded_rect(canvas, x1, y1, x2, y2, radius, color):
    canvas.create_arc(x1, y1, x1+2*radius, y1+2*radius, start=90, extent=90, fill=color, outline=color)  # מצייר את הקשת השמאלית-עליונה
    canvas.create_arc(x2-2*radius, y1, x2, y1+2*radius, start=0, extent=90, fill=color, outline=color)  # מצייר את הקשת הימנית-עליונה
    canvas.create_arc(x1, y2-2*radius, x1+2*radius, y2, start=180, extent=90, fill=color, outline=color)  # מצייר את הקשת השמאלית-התחתונה
    canvas.create_arc(x2-2*radius, y2-2*radius, x2, y2, start=270, extent=90, fill=color, outline=color)  # מצייר את הקשת הימנית-התחתונה
    canvas.create_rectangle(x1+radius, y1, x2-radius, y2, fill=color, outline=color)  # מצייר את המלבן האופקי המרכזי
    canvas.create_rectangle(x1, y1+radius, x2, y2-radius, fill=color, outline=color)  # מצייר את המלבן האנכי המרכזי

# משתנה למעקב אחר המצב הנוכחי ("login" להתחברות, או "signup" להרשמה)
current_mode = "login"

# משתנה למעקב האם הסיסמה גלויה (True) או מוסתרת (False)
show_password = False

# משתנים לשמירת נתוני הקלט
username_var = tk.StringVar()  # משתנה מיוחד המכיל את שם המשתמש שהוקלד
password_var = tk.StringVar()  # משתנה מיוחד המכיל את הסיסמה שהוקלדה
confirm_password_var = tk.StringVar()  # משתנה מיוחד המכיל את אימות הסיסמה שהוקלד

# שדות קלט למילוי נתונים
username_entry = tk.Entry(root, textvariable=username_var, font=("Arial", 12), bd=0, bg="white", fg="#333333", relief="flat")  # תיבת טקסט לשם משתמש
password_entry = tk.Entry(root, textvariable=password_var, font=("Arial", 12), bd=0, bg="white", fg="#333333", relief="flat", show="*")  # תיבת טקסט לסיסמה (מוסתרת בכוכביות)
confirm_password_entry = tk.Entry(root, textvariable=confirm_password_var, font=("Arial", 12), bd=0, bg="white", fg="#333333", relief="flat", show="*")  # תיבת טקסט לאימות סיסמה

# משתנים לשמירת האלמנטים הגרפיים של העין והאיקס/אלכסון
eye_btn1 = None  # משתנה עבור רכיב העין בשדה הראשון
eye_btn2 = None  # משתנה עבור רכיב העין בשדה השני
eye_slash1 = None  # משתנה עבור הקו האלכסוני האדום בשדה הראשון
eye_slash2 = None  # משתנה עבור הקו האלכסוני האדום בשדה השני

# פונקציה להצגת/הסתרת הסיסמה (מחליפה מצב עין גלויה / עין עם קו חוצה)
def toggle_password_visibility():
    global show_password  # מציין שאנחנו מעדכנים את המשתנה הגלובלי show_password
    show_password = not show_password  # הופך את המצב מ-False ל-True או מ-True ל-False
    char = "" if show_password else "*"  # אם הסיסמה גלויה התו הוא ריק (גלוי), אחרת כוכבית
    password_entry.config(show=char)  # מעדכן את תצוגת הסיסמה בשדה הראשון
    confirm_password_entry.config(show=char)  # מעדכן את תצוגת הסיסמה בשדה השני
    color = "#1f75de" if show_password else "#777777"  # צבע כחול כשהסיסמה גלויה, צבע אפור כשהיא מוסתרת
    slash_state = "hidden" if show_password else "normal"  # מסתיר את הקו כשהסיסמה גלויה, מציג אותו כשהיא מוסתרת

    if eye_btn1:  # אם העין הראשונה קיימת
        canvas.itemconfig(eye_btn1, fill=color)  # מעדכן את הצבע שלה
    if eye_slash1:  # אם הקו האדום הראשון קיים
        canvas.itemconfig(eye_slash1, state=slash_state)  # מציג או מסתיר את הקו

    if eye_btn2:  # אם העין השנייה קיימת
        canvas.itemconfig(eye_btn2, fill=color)  # מעדכן את הצבע שלה
    if eye_slash2:  # אם הקו האדום השני קיים
        canvas.itemconfig(eye_slash2, state=slash_state)  # מציג או מסתיר את הקו

# פונקציה להצגת המסך המעודכן
def render_screen():
    global eye_btn1, eye_btn2, eye_slash1, eye_slash2, show_password  # שימוש במשתנים גלובליים
    canvas.delete("all")  # ניקוי המשטח מכל הרכיבים שצויירו עליו
    username_var.set("")  # מוחק את הכתוב בשדה שם המשתמש
    password_var.set("")  # מוחק את הכתוב בשדה הסיסמה
    confirm_password_var.set("")  # מוחק את הכתוב בשדה אימות הסיסמה

    # הסתרת הסיסמה כברירת מחדל ברינדור מסך מחדש
    show_password = False  # מחזיר את המצב להסתרה
    password_entry.config(show="*")  # מציג כוכביות בשדה הסיסמה
    confirm_password_entry.config(show="*")  # מציג כוכביות בשדה אימות הסיסמה

    # הסתרת שדה אימות הסיסמה
    confirm_password_entry.place_forget()  # מסתיר את השדה מהמסך

    # --- כותרת ראשית מעוצבת באנגלית מעל הכרטיס המרכזי ---
    canvas.create_text(352, 47, text="🔒 ENCRYPTED SECURITY CAMERA", fill="#042754", font=("Arial", 18, "bold"))  # צל כהה מאחורי הכותרת
    canvas.create_text(350, 45, text="🔒 ENCRYPTED SECURITY CAMERA", fill="white", font=("Arial", 18, "bold"))  # כותרת ראשית בלבן
    canvas.create_text(350, 72, text="SURVEILLANCE & ACCESS CONTROL", fill="#b0d4ff", font=("Arial", 9, "bold"))  # תת-כותרת אלגנטית בתכלת
    canvas.create_line(230, 88, 470, 88, fill="#388bfd", width=2)  # קו מפריד מעוצב בעובי 2 פיקסלים

    if current_mode == "login":
        # כרטיס Login
        draw_rounded_rect(canvas, 170, 155, 530, 595, 25, "#1f75de")  # מצייר את המלבן המעוגל המרכזי
        canvas.create_text(210, 205, text="Login", fill="white", font=("Arial", 28, "bold"), anchor="w")  # כותב את המילה "Login"

        # שם משתמש
        canvas.create_text(210, 250, text="Username", fill="white", font=("Arial", 11, "bold"), anchor="w")  # תווית "Username"
        draw_rounded_rect(canvas, 210, 268, 490, 310, 8, "white")  # רקע לבן לשדה
        username_entry.place(x=218, y=273, width=264, height=32)  # מיקום שדה הקלט לשם המשתמש
        # סיסמה
        canvas.create_text(210, 330, text="Password", fill="white", font=("Arial", 11, "bold"), anchor="w")  # תווית "Password"
        draw_rounded_rect(canvas, 210, 348, 490, 390, 8, "white")  # רקע לבן לשדה
        password_entry.place(x=218, y=353, width=235, height=32)  # מיקום שדה הקלט לסיסמה
        
        # אייקון עין עם קו אלכסוני חוצה (עין מוצלבת בהסתרה)
        eye_btn1 = canvas.create_text(470, 369, text="👁", fill="#777777", font=("Arial", 13))  # מצייר את האייקון עין
        eye_slash1 = canvas.create_line(462, 361, 478, 377, fill="#d93025", width=2, state="normal")  # מצייר קו אדום אלכסוני
        eye_btn2 = None  # אין שדה שני במסך התחברות
        eye_slash2 = None  # אין קו שני במסך התחברות

        # כפתור Sign in
        draw_rounded_rect(canvas, 210, 420, 490, 465, 10, "#082a52")  # מלבן כחול כהה לכפתור
        canvas.create_text(350, 442, text="Sign in", fill="white", font=("Arial", 14, "bold"))  # טקסט הכפתור "Sign in"

        # הודעת סטטוס
        global status_text  # משתנה גלובלי עבור אלמנט הסטטוס
        status_text = canvas.create_text(350, 485, text="", fill="#ffcccc", font=("Arial", 10, "normal"))  # אלמנט טקסט להצגת הודעות

        # מעבר להרשמה
        canvas.create_text(350, 510, text="Don't have an account?", fill="white", font=("Arial", 10, "normal"))  # שאלה
        canvas.create_text(350, 535, text="Sign Up", fill="white", font=("Arial", 11, "bold"))  # כפתור מעבר להרשמה

    else:
        # כרטיס Sign Up
        draw_rounded_rect(canvas, 170, 110, 530, 640, 25, "#1f75de")  # כרטיס מוגדל להרשמה
        canvas.create_text(210, 155, text="Sign Up", fill="white", font=("Arial", 28, "bold"), anchor="w")  # כותב "Sign Up"

        # שם משתמש
        canvas.create_text(210, 195, text="Username", fill="white", font=("Arial", 11, "bold"), anchor="w")  # תווית "Username"
        draw_rounded_rect(canvas, 210, 213, 490, 255, 8, "white")  # רקע לבן לשדה
        username_entry.place(x=218, y=218, width=264, height=32)  # מיקום השדה

        # סיסמה
        canvas.create_text(210, 275, text="Password", fill="white", font=("Arial", 11, "bold"), anchor="w")  # תווית "Password"
        draw_rounded_rect(canvas, 210, 293, 490, 335, 8, "white")  # רקע לבן לשדה
        password_entry.place(x=218, y=298, width=235, height=32)  # מיקום השדה
        eye_btn1 = canvas.create_text(470, 314, text="👁", fill="#777777", font=("Arial", 13))  # עין ראשונה
        eye_slash1 = canvas.create_line(462, 306, 478, 322, fill="#d93025", width=2, state="normal")  # קו אדום ראשון

        # אימות סיסמה
        canvas.create_text(210, 355, text="Confirm Password", fill="white", font=("Arial", 11, "bold"), anchor="w")  # תווית אימות סיסמה
        draw_rounded_rect(canvas, 210, 373, 490, 415, 8, "white")  # רקע לבן לשדה
        confirm_password_entry.place(x=218, y=378, width=235, height=32)  # מיקום השדה
        eye_btn2 = canvas.create_text(470, 394, text="👁", fill="#777777", font=("Arial", 13))  # עין שנייה
        eye_slash2 = canvas.create_line(462, 386, 478, 402, fill="#d93025", width=2, state="normal")  # קו אדום שני

        # כפתור Register
        draw_rounded_rect(canvas, 210, 445, 490, 490, 10, "#082a52")  # כפתור מלבני מעוגל
        canvas.create_text(350, 467, text="Register", fill="white", font=("Arial", 14, "bold"))  # טקסט "Register"

        # הודעת סטטוס
        status_text = canvas.create_text(350, 515, text="", fill="#ffcccc", font=("Arial", 10, "normal"))  # אלמנט הודעות

        # מעבר להתחברות
        canvas.create_text(350, 550, text="Already have an account?", fill="white", font=("Arial", 10, "normal"))  # שאלה
        canvas.create_text(350, 575, text="Sign In", fill="white", font=("Arial", 11, "bold"))  # מעבר להתחברות
        #----------------------------------------------------------

# שליחת הטופס לשרת
def submit_form(event=None):
    username = username_var.get().strip()  # מוציא את הטקסט משדה שם המשתמש ומנקה רווחים
    password = password_var.get().strip()  # מוציא את הטקסט משדה הסיסמה ומנקה רווחים

    if not username or not password:  # בודק אם אחד השדות נשאר ריק
        canvas.itemconfig(status_text, text="Please enter username and password", fill="#ffcccc")  # הודעה באדום
        return  # עוצר את הפונקציה

    if current_mode == "signup":  # אם מדובר בהרשמה
        confirm = confirm_password_var.get().strip()  # מוציא את הטקסט משדה האימות
        if not confirm:  # אם השדה ריק
            canvas.itemconfig(status_text, text="Please confirm your password", fill="#ffcccc")  # הודעה באדום
            return  # עוצר
        if password != confirm:  # אם הסיסמאות אינן תואמות
            canvas.itemconfig(status_text, text="Passwords do not match!", fill="#ffcccc")  # הודעה באדום
            return  # עוצר

    action = "login" if current_mode == "login" else "register"

    try:
        canvas.itemconfig(status_text, text="Connecting to server...", fill="white")
        root.update()

        # שולח בקשת JSON דרך TCP ל-tcp_server.py
        res_data = send_request(action, username, password)

        if res_data.get("code") == 200:
            msg = "Login Successful!" if current_mode == "login" else "Account Created Successfully!"
            canvas.itemconfig(status_text, text=msg, fill="#88ff88")
        else:
            canvas.itemconfig(status_text, text=res_data.get("message", "Error"), fill="#ffcccc")

    except (OSError, RuntimeError, ValueError):
        canvas.itemconfig(status_text, text="Cannot connect to server", fill="#ffcccc")

  #----------------------------------------------------------------------------
 
# מעבר בין מצבים (התחברות <-> הרשמה)
def toggle_mode():
    global current_mode  # שימוש במשתנה המצב הגלובלי
    current_mode = "signup" if current_mode == "login" else "login"  # מחליף את המצב
    render_screen()  # קורא לרינדור מחדש של המסך

# זיהוי לחיצות עכבר על ה-Canvas
def on_canvas_click(e):
    if current_mode == "login":
        # לחיצה על כפתור העין להצגת/הסתרת סיסמה
        if 450 < e.x < 488 and 348 < e.y < 390:  # בודק אם הלחיצה בתוך תחום העין
            toggle_password_visibility()  # מפעיל את שינוי התצוגה
        elif 210 < e.x < 490 and 420 < e.y < 465:  # בודק אם הלחיצה בתוך כפתור Sign in
            submit_form()  # מפעיל את שליחת הטופס
        elif 290 < e.x < 410 and 520 < e.y < 550:  # בודק אם הלחיצה בתוך טקסט Sign Up
            toggle_mode()  # עובר למסך הרשמה
    else:  # signup
        # לחיצה על כפתור העין בשני השדות
        if 450 < e.x < 488 and (293 < e.y < 335 or 373 < e.y < 415):  # בודק אם הלחיצה בתוך תחום העיניים
            toggle_password_visibility()  # מפעיל את שינוי התצוגה
        elif 210 < e.x < 490 and 445 < e.y < 490:  # בודק אם הלחיצה בתוך כפתור Register
            submit_form()  # מפעיל את שליחת הטופס
        elif 290 < e.x < 410 and 560 < e.y < 590:  # בודק אם הלחיצה בתוך טקסט Sign In
            toggle_mode()  # עובר למסך התחברות
            
# קישור מקשים ועכבר

canvas.bind("<Button-1>", on_canvas_click)

# הפעלת התחברות בלחיצה על Enter
username_entry.bind("<Return>", submit_form)
password_entry.bind("<Return>", submit_form)
confirm_password_entry.bind("<Return>", submit_form)

# הצגת המסך הראשוני
render_screen()

# הפעלת החלון
root.mainloop()