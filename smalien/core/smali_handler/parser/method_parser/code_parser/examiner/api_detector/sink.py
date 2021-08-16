# -*- coding: utf-8 -*-
#
#----------------------------------------------------------------
#
#    VTDroid
#    Copyright (C) 2021  Nagoya Institute of Technology, Hiroki Inayoshi
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>."
#
#----------------------------------------------------------------
#

sink = [
    # URL
    'Ljava/net/URL;-><init>(',
    # Apache
    'Lorg/apache/http/client/methods/HttpGet;-><init>(',
    'Lorg/apache/http/client/methods/HttpPost;-><init>(',
    'Lorg/apache/http/client/entity/UrlEncodedFormEntity;-><init>(',
    'Lorg/apache/http/message/BasicNameValuePair;-><init>(',
    'Lorg/apache/http/entity/StringEntity;-><init>(',
    # String Request
    'Lcom/android/volley/toolbox/StringRequest;-><init>(',
    # OkHttp3
    'Lokhttp3/Request/Builder;-><init>(',
    'Lokhttp3/RequestBody;->',
    # OutputStream
    'Ljava/io/OutputStream;->write(',
    # ByteArrayOutputStream
    'Ljava/io/ByteArrayOutputStream;->write(',
    #  'Ljava/io/ByteArrayOutputStream;->writeTo(Ljava/io/OutputStream;)V',
    # ByteArrayInputStream
    'Ljava/io/ByteArrayInputStream;-><init>(',
    # FileOutputStream
    'Ljava/io/FileOutputStream;->write(',
    # FilterOutputStream
    'Ljava/io/FilterOutputStream;->write(',
    # ObjectOutputStream
    'Ljava/io/ObjectOutputStream;->write',
    # PipedOutputStream
    'Ljava/io/PipedOutputStream;->write(',
    # AssetFileDescriptor.AutoCloseOutputStream
    'Landroid/content/res/AssetFileDescriptor/AutoCloseOutputStream;->write(',
    # Base64OutputStream
    'Landroid/util/Base64OutputStream;->write(',
    # BufferedOutputStream
    'Ljava/io/BufferedOutputStream;->write(',
    # CheckedOutputStream
    'Ljava/util/zip/CheckedOutputStream;->write(',
    # CipherOutputStream
    'Ljavax/crypto/CipherOutputStream;->write(',
    # DataOutputStream
    'Ljava/io/DataOutputStream;->write',
    # DeflaterOutputStream
    'Ljava/util/zip/DeflaterOutputStream;->write(',
    # DigestOutputStream
    'Ljava/security/DigestOutputStream;->write(',
    # GZIPOutputStream
    'Ljava/util/zip/GZIPOutputStream;->write(',
    # InflaterOutputStream
    'Ljava/util/zip/InflaterOutputStream;->write(',
    # JarOutputStream (No method)
    # ParcelFileDescriptor.AutoCloseOutputStream (No method)
    # PrintStream
    'Ljava/io/PrintStream;->print',
    'Ljava/io/PrintStream;->write(',
    # ZipOutputStream
    'Ljava/util/zip/ZipOutputStream;->write(',

    # Writer
    'Ljava/io/Writer;->write(',
    # BufferedWriter
    'Ljava/io/BufferedWriter;->write(',
    # CharArrayWriter
    'Ljava/io/CharArrayWriter;->write(',
    #  'Ljava/io/CharArrayWriter;->writeTo(Ljava/io/Writer;)V',
    # FilterWriter
    'Ljava/io/FilterWriter;->write(',
    # OutputStreamWriter
    'Ljava/io/OutputStreamWriter;->write(',
    # PipedWriter
    'Ljava/io/PipedWriter;->write(',
    # PrintWriter
    'Ljava/io/PrintWriter;->print',
    'Ljava/io/PrintWriter;->write(',
    # StringWriter
    'Ljava/io/StringWriter;->write(',
    # FileWriter
    'Ljava/io/FileWriter;->write(',

    # DataOutput
    'Ljava/io/DataOutput;->write',
    # ObjectOutput
    'Ljava/io/ObjectOutput;->write',
]
