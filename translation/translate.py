if __name__ == "__main__":
    import argparse
    import pathlib
    import sys
    ap = argparse.ArgumentParser()
    ap.add_argument("src", help="input .txt file or '-' for STDIN")
    ap.add_argument("-o", "--out", help="save to file")
    ap.add_argument("--model", default="o4-mini")
    args = ap.parse_args()

    from gpt_translate import GPT4OMiniTranslator

    try:
        print(f"Reading input file: {args.src}")
        raw = sys.stdin.read() if args.src == "-" else pathlib.Path(args.src).read_text(encoding='utf-8')
        print(f"Input text length: {len(raw)} characters")
        
        print(f"Initializing translator with model: {args.model}")
        tx = GPT4OMiniTranslator(model=args.model)
        
        print("Starting translation...")
        ja = tx.translate(raw)
        print(f"Translation completed. Output length: {len(ja)} characters")

        if args.out:
            print(f"Saving translation to: {args.out}")
            pathlib.Path(args.out).write_text(ja, encoding='utf-8')
            print("Translation saved successfully")
        else:
            print(ja)
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

