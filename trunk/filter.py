import os, sys
import email
import email.errors
import StringIO
import BeautifulSoup

class UnwantedMail(Exception):
	pass

def log(msg, *args):
	if args:
		msg = msg % args
	print msg

def usage():
	log('%s: src-dir dst-dir', sys.argv[0])
	sys.exit(1)

def html_2_text(html):
	soup = BeautifulSoup.BeautifulSoup(html)

	# remove all CData, processing-instructions, comments and declarations
	unwanted_elements = (
			BeautifulSoup.CData,
			BeautifulSoup.Comment,
			BeautifulSoup.Declaration,
			BeautifulSoup.ProcessingInstruction,
			)
	elements = soup.findAll(text=lambda text: isinstance(text, unwanted_elements))
	for element in elements:
		element.extract()

	# remove all unwanted tags
	unwanted_tags = (
			'style',
			)
	for tag in soup.findAll(unwanted_tags):
		tag.extract()

	return soup.getText(' ')

def transform_mail(src_fn, dst_f):
	assert hasattr(dst_f, 'write') and callable(dst_f.write)

	try:
		msg = email.message_from_file(open(src_fn))
	except email.errors.MessageError, e:
		# badly malformed mails
		raise UnwantedMail, str(e)

	# write mail headers
	for header, value in sorted(msg.items()):
		dst_f.write('%s: %s\n' % (header, value))

	# try parse 'text/html' entity first, then 'text/plain'
	is_html = True
	entities = [entity for entity in msg.walk() if 'text/html' == entity.get_content_type()]
	if not entities:
		is_html = False
		entities = [entity for entity in msg.walk() if 'text/plain' == entity.get_content_type()]
	if not entities:
		raise UnwantedMail, 'no entity with content-type "text/html" or "text/plain" found'

	# try convert to ASCII
	entity = entities[0]
	payload = entity.get_payload(decode=True)
	charset = entity.get_content_charset('ascii')

	try:
		if is_html:
			payload = html_2_text(payload)
		if not isinstance(payload, unicode):
			payload = payload.decode(charset)
		payload = payload.encode('ascii')
	except (UnicodeEncodeError, UnicodeDecodeError, LookupError), e:
		raise UnwantedMail, str(e)

	if not payload:
		raise UnwantedMail, 'empty mail'

	# write to dst_f
	dst_f.write('\n')
	dst_f.write(payload)
	dst_f.write('\n')

def filter_mails(src_dir, dst_dir):
	if not os.path.exists(dst_dir):
		os.mkdir(dst_dir)

	src_dir = unicode(src_dir)
	for fn in os.listdir(src_dir):
		src_fn = os.path.join(src_dir, fn)
		dst_fn = os.path.join(dst_dir, fn)

		if os.path.isdir(src_fn):
			filter_mails(src_fn, dst_fn)
		else:
			log('Transforming %s', src_fn)
			dst = StringIO.StringIO()
			try:
				transform_mail(src_fn, dst)
			except UnwantedMail, e:
				log('Discard %s: %s', src_fn, e)
			else:
				open(dst_fn, 'w').write(dst.getvalue())

def main():
	if len(sys.argv) < 3:
		usage()

	src_dir, dst_dir = sys.argv[1:3]
	filter_mails(src_dir, dst_dir)

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		pass

