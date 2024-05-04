from tkinter import *
from tkinter import filedialog, messagebox
from PIL import Image
import numpy as np
import os
import hashlib
from Crypto.Cipher import AES


def encrypt(imagename, password):
    print(imagename)
    plaintext = list()
    plaintextstr = ""

    im = Image.open(imagename)
    pix = im.load()

    width = im.size[0]
    height = im.size[1]

    # break up the image into a list, each with pixel values and then append to a string
    for y in range(0, height):
        for x in range(0, width):
            plaintext.append(pix[x, y])

    # add 100 to each tuple value to make sure each are 3 digits long.
    for i in range(0, len(plaintext)):
        for j in range(0, 3):
            aa = int(plaintext[i][j]) + 100
            plaintextstr = plaintextstr + str(aa)

    # length save for encrypted image reconstruction
    relength = len(plaintext)

    # append dimensions of image for reconstruction after decryption
    plaintextstr += "h" + str(height) + "h" + "w" + str(width) + "w"

    # make sure that plantextstr length is a multiple of 16 for AES.  if not, append "n".
    while (len(plaintextstr) % 16 != 0):
        plaintextstr = plaintextstr + "n"

    # encrypt plaintext
    obj = AES.new(password, AES.MODE_CBC, b'This is an IV456')
    ciphertext = obj.encrypt(plaintextstr.encode('utf-8'))

    # write ciphertext to file for analysis
    cipher_name = imagename + ".crypt"
    with open(cipher_name, 'wb') as g:
        g.write(ciphertext)
    print("Encryption Done")


def decrypt(ciphername, password):
    with open(ciphername, 'rb') as cipher:
        ciphertext = cipher.read()

    # decrypt ciphertext with password
    obj2 = AES.new(password, AES.MODE_CBC, b'This is an IV456')
    decrypted = obj2.decrypt(ciphertext)

    # parse the decrypted text back into integer string
    decrypted = decrypted.replace(b"n", b"")

    # extract dimensions of images
    newwidth = decrypted.split(b"w")[1]
    newheight = decrypted.split(b"h")[1]

    # replace height and width with emptyspace in decrypted plaintext
    heightr = b"h" + newheight + b"h"
    widthr = b"w" + newwidth + b"w"
    decrypted = decrypted.replace(heightr, b"")
    decrypted = decrypted.replace(widthr, b"")

    # reconstruct the list of RGB tuples from the decrypted plaintext
    step = 3
    finaltextone = [decrypted[i:i + step] for i in range(0, len(decrypted), step)]
    finaltexttwo = [(int(finaltextone[int(i)]) - 100, int(finaltextone[int(i + 1)]) - 100,
                     int(finaltextone[int(i + 2)]) - 100) for i in range(0, len(finaltextone), step)]

    # reconstruct image from list of pixel RGB tuples
    newim = Image.new("RGB", (int(newwidth), int(newheight)))
    newim.putdata(finaltexttwo)
    img = newim.save("visual_decrypt.jpeg")
    print("Visual Decryption done......")
    return os.path.abspath("visual_decrypt.jpeg")


def rubiks_encrypt(imagename, key, password, filename):
    print(imagename, filename, sep="\n")
    im = Image.open(imagename)
    pixels = np.array(im)

    # Generate a permutation based on the key
    hash_key = hashlib.sha256(key.encode()).digest()
    truncated_seed = int.from_bytes(hash_key[:4], byteorder='big')  # Truncate to fit within 32 bits
    np.random.seed(truncated_seed)
    perm = np.random.permutation(pixels.shape[0] * pixels.shape[1])

    # Shuffle each layer of the image based on the permutation
    print(pixels.shape)
    for i in range(pixels.shape[2]):
        pixels[:, :, i] = pixels[:, :, i].flatten()[perm].reshape(pixels[:, :, i].shape)

    # Convert the modified pixels array back to an image
    encrypted_image = Image.fromarray(pixels)
    encrypted_image.save("rubiks_encrypted_" + filename)
    encrypted_image_imagename = os.path.abspath("rubiks_encrypted_" + filename)
    print(encrypted_image_imagename)
    encrypt(encrypted_image_imagename, password.encode('utf-8'))


def rubiks_decrypt(encrypted_imagename, key, password, filename):
    img = decrypt(encrypted_imagename, password.encode('utf-8'))
    encrypted_im = Image.open(img)
    encrypted_pixels = np.array(encrypted_im)

    # Generate a permutation based on the key
    hash_key = hashlib.sha256(key.encode()).digest()
    truncated_seed = int.from_bytes(hash_key[:4], byteorder='big')  # Truncate to fit within 32 bits
    np.random.seed(truncated_seed)
    perm = np.random.permutation(encrypted_pixels.shape[0] * encrypted_pixels.shape[1])

    # Reverse the shuffle operation for each layer of the image
    for i in range(encrypted_pixels.shape[2]):
        encrypted_pixels[:, :, i] = encrypted_pixels[:, :, i].flatten()[np.argsort(perm)].reshape(
            encrypted_pixels[:, :, i].shape)

    # Convert the modified encrypted_pixels array back to an image
    decrypted_image = Image.fromarray(encrypted_pixels)
    print("rubiks_decrypted_" + ".".join(filename.split('.')[:-1]))
    decrypted_image.save("rubiks_decrypted_" + ".".join(filename.split('.')[:-1]))


def pass_alert():
    messagebox.showinfo("Password Alert", "Please enter a password.")


def rubiks_encrypt_image_open():
    global passg, passg_aes

    enc_pass = passg.get()
    enc_pass_aes = passg_aes.get()
    if enc_pass == "" or enc_pass_aes == "":
        pass_alert()
    else:
        filename = filedialog.askopenfilename()
        rubiks_encrypt(filename, enc_pass, enc_pass_aes, os.path.basename(filename))
        messagebox.showinfo("Success", "Encrypted Image: " + filename)


def rubiks_decrypt_image_open():
    global passg, passg_aes

    dec_pass = passg.get()
    dec_pass_aes = passg_aes.get()
    if dec_pass == "" or dec_pass_aes == "":
        pass_alert()
    else:
        filename = filedialog.askopenfilename()
        rubiks_decrypt(filename, dec_pass, dec_pass_aes, os.path.basename(filename))
        messagebox.showinfo("Success", "Decrypted Image: " + filename)


class App:
    def __init__(self, master):
        global passg, passg_aes
        title = "Dual Encryption Project"
        author = "Mini -- Project"
        msgtitle = Message(master, text=title)
        msgtitle.config(font=('helvetica', 17, 'bold'), width=200)
        msgauthor = Message(master, text=author)
        msgauthor.config(font=('helvetica', 10), width=200)

        canvas_width = 200
        canvas_height = 50
        w = Canvas(master,
                   width=canvas_width,
                   height=canvas_height)
        msgtitle.pack()
        msgauthor.pack()
        w.pack()

        passlabel = Label(master, text="Enter Rubik's Key:")
        passlabel.pack()
        passg = Entry(master, show="*", width=20)
        passg.pack()

        passlabel_aes = Label(master, text="Enter AES Key:")
        passlabel_aes.pack()
        passg_aes = Entry(master, show="*", width=20)
        passg_aes.pack()

        self.encrypt = Button(master,
                              text="Encrypt", fg="black",
                              command=rubiks_encrypt_image_open, width=25, height=5)
        self.encrypt.pack(side=LEFT)
        self.decrypt = Button(master,
                              text="Decrypt", fg="black",
                              command=rubiks_decrypt_image_open, width=25, height=5)
        self.decrypt.pack(side=RIGHT)


# Main
root = Tk()
root.wm_title("Image Encryption")
app = App(root)
root.mainloop()
