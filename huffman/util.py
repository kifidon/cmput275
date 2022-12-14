import bitio
import huffman
import pickle


def read_tree(tree_stream):
    '''Read a description of a Huffman tree from the given compressed
    tree stream, and use the pickle module to construct the tree object.
    Then, return the root node of the tree itself.

    Args:
      tree_stream: The compressed stream to read the tree from.

    Returns:
      A Huffman tree root constructed according to the given description.
    '''

    return pickle.load(tree_stream)


def decode_byte(tree, bitreader):
    """
    Reads bits from the bit reader and traverses the tree from
    the root to a leaf. Once a leaf is reached, bits are no longer read
    and the value of that leaf is returned.

    Args:
      bitreader: An instance of bitio.BitReader to read the tree from.
      tree: A Huffman tree.

    Returns:
      Next byte of the compressed bit stream.
    """
    # https://eclass.srv.ualberta.ca/pluginfile.php/8451720/mod_resource/content/15/Huffman_Coding_DND.dec.30.2020.pdf
    if type(tree) == huffman.TreeLeaf:
        return tree.getValue()
    elif bitreader.readbit():
        return decode_byte(tree.getRight(), bitreader)
    else:
        return decode_byte(tree.getLeft(), bitreader)


def decompress(compressed, uncompressed):
    '''First, read a Huffman tree from the 'compressed' stream using your
    read_tree function. Then use that tree to decode the rest of the
    stream and write the resulting symbols to the 'uncompressed'
    stream.

    Args:
      compressed: A file stream from which compressed input is read.
      uncompressed: A writable file stream to which the uncompressed
          output is written.
    '''

    tree = read_tree(compressed)
    mybitreader = bitio.BitReader(compressed)
    my_bytes = []

    end_of_file = False
    while not end_of_file:
        try:
            decoded_byte = decode_byte(tree, mybitreader)
            my_bytes.append(decoded_byte)
        except EOFError:
            end_of_file = True
    my_bitwriter = bitio.BitWriter(uncompressed)

    for b in my_bytes:
        if b is None:
            break
        else:
            my_bitwriter.writebits(b, 8)
    my_bitwriter.flush()


def write_tree(tree, tree_stream):
    '''Write the specified Huffman tree to the given tree_stream
    using pickle.

    Args:
      tree: A Huffman tree.
      tree_stream: The binary file to write the tree to.
    '''

    pickle.dump(tree, tree_stream)


def compress(tree, uncompressed, compressed):
    '''First write the given tree to the stream 'compressed' using the
    write_tree function. Then use the same tree to encode the data
    from the input stream 'uncompressed' and write it to 'compressed'.
    If there are any partially-written bytes remaining at the end,
    write 0 bits to form a complete byte.

    Flush the bitwriter after writing the entire compressed file.

    Args:
      tree: A Huffman tree.
      uncompressed: A file stream from which you can read the input.
      compressed: A file stream that will receive the tree description
          and the coded input data.
    '''

    write_tree(tree, compressed)
    table = huffman.make_encoding_table(tree)

    my_bitreader = bitio.BitReader(uncompressed)
    my_bytes = []

    # This while loop code below was gotten from the help of Johnny zhang
    while True:
        try:
            encoded_byte = table[my_bitreader.readbits(8)]
            byte = []
            for bit in encoded_byte:
                byte.append(bit)
            my_bytes.append(byte)
        except EOFError:
            break

    my_bitwriter = bitio.BitWriter(compressed)
    for byte in my_bytes:
        for b in byte:
            my_bitwriter.writebit(b)
    end_symbol = table[None]
    [my_bitwriter.writebit(b) for b in end_symbol]
    my_bitwriter.flush()
