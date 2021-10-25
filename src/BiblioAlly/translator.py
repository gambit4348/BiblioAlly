from . import domain, basetranslator as bt
import re
from typing import Dict
from .utility import alphanum_crc32

key_names = [
    'Accuvision',
    'Adobe',
    'Aion',
    'Akasha',
    'Alibaba',
    'Amazon',
    'AMD',
    'AnyVision',
    'Apple',
    'APTIV',
    'Arahub',
    'Argo AI',
    'Ariel AI',
    'Australia',
    'BMW',
    'Baidu',
    'Beihang',
    'Bosch',
    'Bytedance',
    'California',
    'Canon',
    'CAS',
    'Chinese Academy of Sciences',
    'Capillary',
    'China',
    'Chinese',
    'CISPA',
    'Clarifai',
    'Clova',
    'Computer Vision Center',
    'Czech Republic',
    'Data61',
    'Dark Matter AI',
    'DarkMatter AI',
    'Department of Computer Science',
    'Facebook',
    'FaceSoft',
    'Facesoft',
    'France',
    'Google',
    'Huawei',
    'Hong Kong',
    'HP Inc',
    'HuaZhong',
    'Ibm',
    'IBM',
    'ICetana',
    'India',
    'INRIA',
    'Intel',
    'Japan',
    'JD.com',
    'Kakao',
    'MAPLE',
    'Max Planck Institute',
    'Megvii',
    'Mexico',
    'Michigan',
    'Microsoft AI',
    'MIT',
    'MPI',
    'NEC',
    'Netherlands',
    'Nvidia',
    'NVIDIA',
    'Oregon',
    'OSGeo',
    'ParisTech',
    'RIKEN',
    'SenseTime',
    'Sensetime',
    'Shanghai',
    'Shenzhen',
    'Siemens',
    'Skolkovo',
    'Slovenia',
    'Spain',
    'Switzerland',
    'Tencent',
    'Turkey',
    'UCLA',
    'United Kingdom',
    'United States',
    'Universal AI',
    'U.S.A',
    'USDA-ARS',
    'Valeo',
    'Vision Semantics',
    'WaveOne',
]
special_names: Dict[str, str] = {
    '12 Sigma Technologies': 'USA',
    '3DGEO': 'Australia',
    'A-STAR': 'Singapore',
    'ACRV': 'Australia',
    'Adobe': 'USA',
    'Aion': 'Canada',
    'Akasha': 'USA',
    'Alibaba': 'China',
    'Amazon': 'USA',
    'AMD': 'USA',
    'Analytics and Data Science Institute': 'USA',
    'AnyVision': 'Israel',
    'Apple': 'USA',
    'APTIV': 'Ireland',
    'Arahub': 'Poland',
    'Argo AI': 'USA',
    'Ariel AI': 'United Kingdom',
    'Assam': 'India',
    'Baidu': 'China',
    'BCS': 'United Kingdom',
    'Beihang': 'China',
    'BMW': 'Germany',
    'BNRist': 'China',
    'Borealis AI': 'Canada',
    'Bosch': 'Germany',
    'BR': 'Brazil',
    'BUPT': 'China',
    'Bytedance': 'China',
    'CAAC': 'China',
    'CAEIT': 'China',
    'California': 'USA',
    'Caltech': 'USA',
    'Cainiao AI': 'China',
    'Canon': 'Japan',
    'Capillary': 'Singapore',
    'CAS': 'China',
    'Chengdu': 'China',
    'Chinese': 'China',
    'Chinese Academy of Sciences': 'China',
    'CentraleSupélec': 'France',
    'CISPA': 'Germany',
    'Clarifai': 'USA',
    'Clova': 'South Korea',
    'Computer Vision Center': 'Spain',
    'Computer Vision Group': 'Germany',
    'Cornell University': 'USA',
    'CSAIL': 'USA',
    'CSIRO': 'Australia',
    'DeepGlint': 'China',
    'DeepMind': 'United Kingdom',
    'DeepScale': 'USA',
    'Deepwise AI Lab': 'China',
    'Denso IT Laboratory': 'Japan',
    'Department of Electrical and Electronic Engineering EEE': 'Bangladesh',
    'DisneyResearch-Studios': 'Sweden',
    'Dark Matter AI': 'China',
    'DarkMatter AI': 'United Arab Emirates',
    'Darlington': 'Australia',
    'Data61': 'Australia',
    'Department of Computer Science': 'United Kingdom',
    'DGEO': 'Belgium',
    'DJI': 'China',
    'Duke University': 'USA',
    'DUT': 'South Africa',
    'Dyson Robotics Lab': 'United Kingdom',
    'Electronics and Telecommunications Research Institute': 'South Korea',
    'Earth Science Analytics': 'Norway',
    'École Polytechnique': 'France',
    'Egnatia Odos  E': 'Greece',
    'Element AI': 'Canada',
    'Everest Innovation Technology': 'Hong Kong',
    'ES': 'Spain',
    'ExMedio Inc': 'China',
    'Facebook': 'USA',
    'FaceSoft': 'United Kingdom',
    'Facesoft': 'United Kingdom',
    'Faculty of Computational Mathematics and Cybernetics': 'Russian Federation',
    'Fitness Tracking App from Samsung': 'South Korea',
    'Five AI': 'USA',
    'FiveAI': 'USA',
    'Ford Research': 'USA',
    'Fraunhofer Institute of Optronics': 'Germany',
    'Fujitsu Laboratories Ltd': 'Japan',
    'Google': 'USA',
    'GREE Electric Appliances': 'China',
    'Higher School of Economics': 'Russian Federation',
    'HP Inc': 'USA',
    'Huawei': 'China',
    'HuaZhong': 'China',
    'HKUST': 'Hong Kong',
    'HTC Research and Healthcare DeepQ': 'China',
    'Horizon Robotics': 'China',
    'Hyundai MNSOFT': 'South Korea',
    'Ibm': 'USA',
    'IBM': 'USA',
    'ICetana': 'Australia',
    'INRIA': 'France',
    'IMED Biotech Unit': 'China',
    'INDE R and D': 'United Kingdom',
    'Inria': 'France',
    'Institute of Human Centered Engineering': 'Malaysia',
    'Intel': 'USA',
    'AI Research of': 'China',
    'JD AI': 'China',
    'JD Digits': 'China',
    'Kakao': 'South Korea',
    'Korea': 'North Korea',
    'Korea the Republic of': 'North Korea',
    'Magic Leap': 'USA',
    'Lab-STICC': 'France',
    'LG Electronics': 'South Korea',
    'Laboratory for Physical Sciences': 'USA',
    'MAPLE': 'USA',
    'Max Planck Institute': 'Germany',
    'Media and Data Science Research Lab': 'India',
    'Megvii': 'China',
    'Mimyk Medical Simulations  Ltd': 'India',
    'Microsoft': 'USA',
    'Microsoft AI': 'USA',
    'Microsoft Research': 'USA',
    'Microsoft Research Asia': 'China',
    'Microsoft Reserach Asia': 'China',
    'Ministry of Education': 'China',
    'Michigan': 'USA',
    'MIT': 'USA',
    'MPI': 'Germany',
    'MOST Joint Research Center for AI Technology and All Vista Healthcare': 'Taiwan',
    'MVTec Software GmbH': 'Germany',
    'Mapillary Research': 'Sweden',
    'MediaTek': 'Taiwan',
    'Meshcapade': 'Germany',
    'National Institute of Informatics': 'Japan',
    'National Institute of Advanced Industrial Science and Technology': 'Japan',
    'National Police Lab AI': 'Netherlands',
    'National Research University Higher School of Economics': 'Russian Federation',
    'NetEase Fuxi AI Lab': 'China',
    'Northeastern University': 'USA',
    'NAVER LABS': 'South Korea',
    'NAVER LABS Europe': 'France',
    'NEC': 'USA',
    'Niantic': 'USA',
    'Northwestern University': 'USA',
    'Oregon': 'USA',
    'ParisTech': 'France',
    'PARC': 'USA',
    'Pinscreen': 'USA',
    'PRIOR at Allen Institute for AI': 'USA',
    'Peter Munk Cardiac Center': 'Canada',
    'Nvidia': 'USA',
    'NVIDIA': 'USA',
    'OSGeo': 'USA',
    'Qed Software': 'New Zealand',
    'Qihoo  AI Institute': 'China',
    'Qualcomm AI Research': 'USA',
    'Redmond': 'USA',
    'Rice University': 'USA',
    'RIKEN': 'Japan',
    'Saarland Informatics Campus': 'Germany',
    'Salesforce Research': 'USA',
    'Salesforce Research Asia': 'China',
    'Samsung Research America': 'USA',
    'Security Research Labs': 'China',
    'Snap Inc': 'USA',
    'Sesto Robotics': 'Singapore',
    'SenseTime': 'Hong Kong',
    'Sensetime': 'Hong Kong',
    'Shanghai': 'China',
    'Shenzhen': 'China',
    'Siemens': 'Germany',
    'Sigma Technologies': 'Spain',
    'Skolkovo': 'Russian Federation',
    'Skoltech': 'Russian Federation',
    'Solutions': 'USA',
    'Sony Europe': 'United Kingdom',
    'Southern University of Science and Technology': 'China',
    'SRI International': 'USA',
    'Stanford': 'USA',
    'Swisscom': 'Switzerland',
    'TAMU': 'USA',
    'Technion': 'Israel',
    'Tencent': 'China',
    'Tongji University': 'China',
    'Toyota Research Institute': 'USA',
    'Tunisie': 'Tunisia',
    'TuSimple': 'USA',
    'UISEE Technology Inc': 'China',
    'UCL': 'United Kingdom',
    'UCLA': 'USA',
    'Uber Advanced Technologies Group': 'USA',
    'UESTC': 'China',
    'UK': 'United Kingdom',
    'UMass Amherst': 'USA',
    'U.M.B.C.': 'USA',
    'Umbc': 'USA',
    'United States': 'USA',
    'Universal AI': 'USA',
    'United Technologies Research Center': 'Ireland',
    'University of Aveiro': 'Portugal',
    'University of Ljubljana': 'Slovenia',
    'Universidad de Zaragoza': 'Spain',
    'Univrses AB': 'Sweden',
    'UNIST': 'South Korea',
    'UPEM': 'France',
    'U.S.A': 'USA',
    'USC Institute for Creative Technologies': 'USA',
    'USDA-ARS': 'USA',
    'USTC': 'China',
    'UIUC': 'USA',
    'UISEE Technology': 'China',
    'Vaitl Inc': 'USA',
    'Vision Semantics': 'United Kingdom',
    'Visual Narrative Initiative': 'USA',
    'WA': 'USA',
    'VMware Research': 'USA',
    'Valeo': 'France',
    'WaveOne': 'USA',
    'Xnor.ai': 'USA',
    'Yahoo Research': 'USA',
    'Zebra Medical Vision': 'Israel',
    'Zoox': 'USA',
    'ECNU': 'China',
    'EPFL': 'France',
    'IRISA': 'France',
    'Inc': 'USA',
    'MILA': 'Canada',
    'NTNU': 'Norway',
    'Unitary': 'United Kingdom',
    'Accuvision': 'Taiwan',
    'Department of ECE': 'India',
    'ENS Cachan': 'France',
    'ETRI': 'Sounth Korea',
    'Foundry': 'Australia',
    'ICT': 'China',
    'IITP': 'Russian Federation',
    'KPST': 'Sounth Korea',
    'LLC': 'USA',
    'NUS': 'Singapore',
    'POSTECH': 'South Korea',
}


class Translator(bt.BaseTranslator):
    kinds = {
        'conference': 'proceedings',
        'inproceedings': 'proceedings',
    }

    def documents_from_file(self, filename):
        with open(filename, "r", encoding="utf-8") as texFile:
            if texFile.mode != "r":
                return {}
            content = texFile.read()
        proto_documents = self._proto_documents_from_content(content)
        documents = self._documents_from_proto_documents(proto_documents)
        return documents

    def bibtext_from_documents(self, documents):
        proto_documents = self._proto_documents_from_documents(documents)
        bibtexts = [self._as_bibtex(pd) for pd in proto_documents]
        return '\n'.join(bibtexts)

    def _as_bibtex(self, proto_document):
        kind = proto_document['type']
        fields = proto_document['fields']
        external_key = fields['external_key']
        del fields['external_key']
        key_value = []
        for key, value in fields.items():
            key_value.append(f'{key} = {value}')
        bibtex = f'@{kind}' + '{' + f'{external_key}\n' + ',\n'.join(key_value) + '\n}\n'
        return bibtex

    def _documents_from_proto_documents(self, proto_documents):
        documents = []
        for proto_document in proto_documents:
            document = self._document_from_proto_document(proto_document)
            document.title_crc32 = alphanum_crc32(document.title)
            documents.append(document)
        return documents

    def _proto_documents_from_documents(self, documents):
        proto_documents = []
        for document in documents:
            proto_document = self._proto_document_from_document(document)
            proto_documents.append(proto_document)
        return proto_documents

    @staticmethod
    def _translate_kind(proto_document):
        kind = proto_document['type'].strip().lower()
        if kind in Translator.kinds:
            proto_document['type'] = Translator.kinds[kind]

    @staticmethod
    def _expand_affiliations(affiliations, authors):
        if affiliations is None:
            new_affiliations = []
            for index, author in enumerate(authors):
                new_affiliation = domain.DocumentAuthor(author=author, first=index == 0)
                new_affiliations.append(new_affiliation)
            return new_affiliations

        author_affi = {}
        for affiliation in affiliations:
            if affiliation.institution is None:
                continue
            names = affiliation.institution.name.strip().split('; ')
            parts = names[len(names) - 1].split(', ')
            description = ', '.join(parts[2:])
            names[len(names) - 1] = ', '.join(parts[0:2])
            for name in names:
                author_affi[name] = (description, affiliation.institution.country)
        new_affiliations = []
        for index, author in enumerate(authors):
            affi = None
            if author.long_name in author_affi:
                affi = author_affi[author.long_name]
            elif author.short_name in author_affi:
                affi = author_affi[author.short_name]
            if affi is not None:
                new_institution = domain.Institution(name=affi[0], country=affi[1])
                new_affiliation = domain.DocumentAuthor(author=author, institution=new_institution, first=index == 0)
            else:
                new_affiliation = domain.DocumentAuthor(author=author, first=index == 0)
            new_affiliations.append(new_affiliation)
        return new_affiliations

    @staticmethod
    def _proto_documents_from_content(content):
        proto_documents = []
        lines = content.split('\n')
        proto_document = {}
        fields = {}
        complete_entry = True
        entry_pieces = []
        for line in lines:
            if len(line) == 0:
                continue
            if line[0] == '@':
                if len(fields) > 0:
                    proto_document['field'] = fields
                    proto_documents.append(proto_document)
                    proto_document = {}
                    fields = {}
                index = line.find('{')
                proto_document['type'] = line[1:index].lower()
                proto_document['id'] = line[index + 1:-2]
            else:
                if complete_entry:
                    complete_entry = (line[-2:] == '},' or line[-1] == '}')
                    if not complete_entry:
                        entry_pieces.append(line.strip())
                    else:
                        index = line.find('=')
                        fields[line[0:index].strip()] = Translator._all_uncurly(line[index + 1:-2].strip())
                else:
                    entry_pieces.append(line.strip())
                    complete_entry = (line[-2:] == '},' or line[-1] == '}')
                    if complete_entry:
                        entry = ' '.join(entry_pieces)
                        index = entry.find('=')
                        fields[entry[0:index].strip()] = Translator._all_uncurly(entry[index + 1:-2].strip())
                        entry_pieces = []

        return proto_documents

    def bibtex_from_document(self, ref):
        return ''

    def _document_from_proto_document(self, proto_document):
        return None

    def _proto_document_from_document(self, document):
        return dict()

    @staticmethod
    def _all_uncurly(value):
        return re.sub('[{}]', '', value)

    def _affiliations_from_field(self, affiliations_field, separator='; '):
        affiliations = []
        affiliation_pieces = affiliations_field.replace('&amp;', '&').split(separator)
        for affiliation_piece in affiliation_pieces:
            if affiliation_piece[-1] == '.':
                parts = re.sub('[()]', '', affiliation_piece[0:-1]).split(', ')
            else:
                parts = re.sub('[()]', '', affiliation_piece).split(', ')
            count = len(parts)

            while count > 0:
                words = parts[count - 1].split(' ')
                word_count = len(words)
                for word_index, word in enumerate(words):
                    if not self._is_name(word):
                        words[word_index] = ''
                parts[count - 1] = ' '.join(words).strip()
                if len(parts[count - 1].strip()) == 0:
                    count -= 1
                if self._is_name(parts[count - 1]):
                    break
                count -= 1
            if count == 0:
                parts = re.sub('[()]', '', affiliation_piece).split(', ')
                count = len(parts)

            institution_name = ', '.join(parts[0:count - 1])
            institution_country = parts[count - 1]
            parts = institution_country.split(' ')
            if len(parts) > 1:
                last_part = parts[len(parts) - 1]
                if last_part == 'USA':
                    institution_country = last_part
                    institution_name = institution_name + ', ' + ' '.join(parts[0:len(parts) - 2])
            part_index = institution_country.find('e-mail:')
            if part_index > -1:
                institution_country = institution_country[0:part_index - 1].strip()
            for key_name in key_names:
                if institution_country.find(key_name) > -1:
                    institution_country = key_name
                    break
            if institution_country in special_names:
                if institution_name == '':
                    institution_name = institution_country
                else:
                    institution_name = institution_name + ', ' + institution_country
                institution_country = special_names[institution_country]
            institution = domain.Institution(name=institution_name, country=institution_country)
            affiliations.append(domain.DocumentAuthor(institution=institution, first=len(affiliations) == 0))
        return affiliations

    @staticmethod
    def _authors_from_field(author_field, use_long_as_short=False):
        author_field = author_field.replace("\\", "").replace("'", "").replace('"', "").replace('{', ""). \
            replace('}', "")
        author_names = author_field.split(' and ')
        if len(author_names) == 0:
            author_names = ['Author, Unamed']
        for i in range(len(author_names)):
            if Translator._is_direct_name(author_names[i]):
                author_names[i] = Translator._reversed_name(author_names[i])

        authors = []
        inserted_names = []
        for authorName in author_names:
            if use_long_as_short:
                short_name = authorName.strip()
            else:
                short_name = domain.Author.short_name_from_name(authorName.strip())
            if short_name in inserted_names:
                continue
            inserted_names.append(short_name)
            long_name = authorName.strip()
            author = domain.Author(short_name, long_name)
            authors.append(author)
        return authors

    @staticmethod
    def _curly(value: str, separator: str = ",", rep: int = 1) -> str:
        if type(value) is list:
            curly_value = "{"*rep + separator.join(value) + "}"*rep
        else:
            curly_value = "{"*rep + value + "}"*rep
        return curly_value

    @staticmethod
    def _is_name(value):
        for c in value:
            if not (c.isalpha() or c == ' ' or c == "'" or c == '-'):
                return False
        return True

    @staticmethod
    def _is_direct_name(name):
        return ',' not in name

    @staticmethod
    def _reversed_name(name):
        pieces = name.split()
        if len(pieces) > 1:
            return pieces[-1] + ', ' + ' '.join(pieces[0:len(pieces)-1])
        else:
            return name

    @staticmethod
    def _uncurlied(value):
        if len(value) == 0:
            return value
        if value[0] == '{':
            start = 1
        else:
            start = 0
        if value[len(value) - 1] == '}':
            end = len(value) - 1
        else:
            end = len(value)
        return value[start:end]
