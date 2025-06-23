import pygame
import sys

# Initialize Pygame
pygame.init()

# Define screen dimensions
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Banking System")

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 100)
DARK_GREEN = (0, 170, 80)
RED = (200, 50, 50)
DARK_RED = (170, 30, 30)
BLUE = (50, 150, 255)
DARK_BLUE = (30, 120, 230)
GRAY = (200, 200, 200)

# Fonts
FONT = pygame.font.SysFont('Arial', 24)

# Animation utility for fade effects
def fade_in_text(surface, text, font, color, x, y, center=False, duration=1000):
    alpha_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    for alpha in range(0, 256, 5):  # Gradually increase alpha
        alpha_surface.fill((255, 255, 255, alpha))
        surface.fill(WHITE)
        draw_text(text, font, color, surface, x, y, center=center)
        surface.blit(alpha_surface, (0, 0))
        pygame.display.update()
        pygame.time.delay(duration // 51)  # Duration split into 51 frames

# Button class for interactive buttons with hover animation
class Button:
    def __init__(self, x, y, width, height, color, hover_color, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hover_color = hover_color
        self.text = text
        self.scale = 1.0  # Scaling factor for hover animation

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.rect.collidepoint(mouse_pos)
        color = self.hover_color if is_hovered else self.color
        if is_hovered:
            self.scale = min(self.scale + 0.1, 1.2)
        else:
            self.scale = max(self.scale - 0.1, 1.0)
        # Create a scaled surface for the animation
        scaled_rect = self.rect.inflate((self.scale - 1) * self.rect.width, (self.scale - 1) * self.rect.height)
        pygame.draw.rect(surface, color, scaled_rect, border_radius=10)
        draw_text(self.text, FONT, WHITE, surface, scaled_rect.centerx, scaled_rect.centery, center=True)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            return True
        return False

# BankAccount class
class BankAccount:
    no_of_cust = 0

    def __init__(self, name, mobile_no, initial_depo, pin):
        self.name = name
        self.mobile_no = mobile_no
        self.balance = initial_depo
        self.pin = pin
        self.cust_acc_num = BankAccount.no_of_cust + 1
        BankAccount.no_of_cust += 1

    def basic_details(self):
        return f"Name: {self.name}, Account No: {self.cust_acc_num}, Balance: {self.balance}"

    def withdraw(self, amount):
        if amount <= 0:
            return "Invalid amount!"
        if amount > self.balance:
            return "Insufficient balance!"
        self.balance -= amount
        return f"Withdrawal successful! New balance: {self.balance}"

    def transfer(self, recipient, amount):
        if amount <= 0:
            return "Invalid amount!"
        if amount > self.balance:
            return "Insufficient balance!"
        self.balance -= amount
        recipient.balance += amount
        return f"Transfer successful! Your new balance: {self.balance}"

# Function to display text
def draw_text(text, font, color, surface, x, y, center=False):
    label = font.render(text, True, color)
    if center:
        x -= label.get_width() // 2
        y -= label.get_height() // 2
    surface.blit(label, (x, y))

# Function to get text input from the user
def get_text_input(prompt, x, y):
    input_box = pygame.Rect(x - 150, y, 300, 40)
    color_inactive = GRAY
    color_active = DARK_BLUE
    color = color_inactive
    text = ''
    active = False
    clock = pygame.time.Clock()
    
    while True:
        screen.fill(WHITE)
        draw_text(prompt, FONT, BLACK, screen, SCREEN_WIDTH // 2, y - 50, center=True)
        pygame.draw.rect(screen, color, input_box, border_radius=5)
        draw_text(text, FONT, BLACK, screen, input_box.x + 10, input_box.y + 5)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                active = input_box.collidepoint(event.pos)
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN and active:
                if event.key == pygame.K_RETURN:
                    return text.strip()
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                else:
                    text += event.unicode
        clock.tick(30)

# Main program
def main():
    customer_dict = {}

    # Utility function to display a message with animation
    def show_message(message):
        fade_in_text(screen, message, FONT, BLACK, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, center=True, duration=1000)
        pygame.time.wait(1000)

    # Create a new account
    def create_account():
        name = get_text_input("Enter your name:", SCREEN_WIDTH // 2, 100)
        try:
            mobile_no = int(get_text_input("Enter your mobile number:", SCREEN_WIDTH // 2, 150))
            initial_depo = int(get_text_input("Enter your initial deposit:", SCREEN_WIDTH // 2, 200))
            pin = int(get_text_input("Create a PIN:", SCREEN_WIDTH // 2, 250))
            if initial_depo <= 0:
                show_message("Initial deposit must be positive!")
                return
        except ValueError:
            show_message("Invalid input! Please try again.")
            return

        customer = BankAccount(name, mobile_no, initial_depo, pin)
        customer_dict[customer.cust_acc_num] = customer
        show_message(f"Account created! Your account number is {customer.cust_acc_num}")

    # Login to an existing account
    def login_account():
        try:
            account_no = int(get_text_input("Enter your account number:", SCREEN_WIDTH // 2, 100))
            pin = int(get_text_input("Enter your PIN:", SCREEN_WIDTH // 2, 150))
        except ValueError:
            show_message("Invalid input! Please try again.")
            return

        if account_no in customer_dict and customer_dict[account_no].pin == pin:
            account_menu(customer_dict[account_no])
        else:
            show_message("Invalid account number or PIN!")

    # Account menu after login
    def account_menu(account):
        buttons = [
            Button(200, 100, 200, 50, GREEN, DARK_GREEN, "Withdraw"),
            Button(200, 200, 200, 50, BLUE, DARK_BLUE, "Transfer"),
            Button(200, 300, 200, 50, RED, DARK_RED, "Logout")
        ]
        while True:
            screen.fill(WHITE)

             # Display the current balance at the top
            draw_text(f"Welcome, {account.name}!", FONT, BLACK, screen, SCREEN_WIDTH // 2, 20, center=True)
            draw_text(f"Account Balance: {account.balance}", FONT, BLACK, screen, SCREEN_WIDTH // 2, 60, center=True)


            for button in buttons:
                button.draw(screen)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                for button in buttons:
                    if button.is_clicked(event):
                        if button.text == "Withdraw":
                            try:
                                amount = int(get_text_input("Enter amount to withdraw:", SCREEN_WIDTH // 2, 100))
                                show_message(account.withdraw(amount))
                            except ValueError:
                                show_message("Invalid amount!")
                        elif button.text == "Transfer":
                            try:
                                recipient_acc = int(get_text_input("Enter recipient account number:", SCREEN_WIDTH // 2, 100))
                                if recipient_acc in customer_dict:
                                    amount = int(get_text_input("Enter amount to transfer:", SCREEN_WIDTH // 2, 150))
                                    show_message(account.transfer(customer_dict[recipient_acc], amount))
                                else:
                                    show_message("Recipient account not found!")
                            except ValueError:
                                show_message("Invalid input!")
                        elif button.text == "Logout":
                            return

    # Buttons for the main menu
    buttons = [
        Button(200, 100, 200, 50, BLUE, DARK_BLUE, "Create Account"),
        Button(200, 200, 200, 50, GREEN, DARK_GREEN, "Login Account"),
        Button(200, 300, 200, 50, RED, DARK_RED, "Exit")
    ]

    # Main loop
    running = True
    while running:
        screen.fill(WHITE)
        draw_text("Banking System", FONT, BLACK, screen, SCREEN_WIDTH // 2, 50, center=True)
        for button in buttons:
            button.draw(screen)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            for button in buttons:
                if button.is_clicked(event):
                    if button.text == "Create Account":
                        create_account()
                    elif button.text == "Login Account":
                        login_account()
                    elif button.text == "Exit":
                        running = False

    pygame.quit()
    sys.exit()

# Run the main program
main()
